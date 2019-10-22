""" Logic for validation of submissions made to the tournament """

import json
import os
import re
import subprocess
from datetime import datetime
from enum import Enum
from itertools import takewhile

from tournament import daemon
from tournament.config import AssignmentConfig, ApprovedSubmitters, SubmitterExtensions
from tournament.config.assignments import AbstractAssignment
from tournament.flags import get_flag, set_flag, clear_all_flags, SubmissionFlag
from tournament.util import paths, format as fmt, print_tourney_trace
from tournament.util.types import FilePath, Prog, Result, Submitter, TestResult


class Stage(Enum):
    """
    Specifies the order in which submission validation stages must be performed.
    The value of the enum is the SubmissionFlag that is set on successful completion of the stage
    """
    CHECK_ELIG = SubmissionFlag.ELIG
    COMPILE = SubmissionFlag.COMPILED
    VALIDATE_TESTS = SubmissionFlag.TESTS_VALID
    VALIDATE_PROGS = SubmissionFlag.PROGS_VALID
    SUBMIT = None

    def prev_stage(self):
        """ Get the preceding stage. e.g. COMPILE returns CHECK_ELIG """
        if self.name == Stage.CHECK_ELIG.name:  # pylint: disable=comparison-with-callable
            return self

        values = list(Stage.__members__.keys())
        prev_name = values[values.index(self.name) - 1]
        return Stage.__members__.get(prev_name)


def run_stage(stage: Stage, submitter: Submitter, assg_name: str = None, submission_dir: FilePath = None) -> Result:
    """
    Run a testing stage in the submission pipeline
    :param stage: which testing stage to run on the submission
    :param submitter: the submitters whose submission is being tested
    :param assg_name: the name of the assignment being tested
    :param submission_dir: the directory of the submission. This is only used for `check_elig`. Afterwards a copy of
                           the submission is located in the pre_validation directory
    :return: the result of running the test stage
    """

    _, pre_val_dir, _ = _submission_details(submitter)

    # Check that the test stage can be run.
    # It should only be run if directly preceded by the stage defined in the Stage enum
    if stage == Stage.CHECK_ELIG or get_flag(stage.prev_stage().value, pre_val_dir):
        clear_all_flags(pre_val_dir)
    else:
        # Find the next stage that should be run
        elig_stages = [st.name for st in reversed(Stage) if get_flag(st.prev_stage().value, pre_val_dir)]
        should_run = elig_stages[0] if elig_stages else Stage.CHECK_ELIG.name
        return Result(False, "Cannot run the {} stage. The {} stage must be run first.\n"
                             "Note: It is recommended that you make a new commit rather than manually rerunning stages "
                             "via the Gitlab web interface".format(stage.name, should_run))

    # run the stage
    result = {Stage.CHECK_ELIG: lambda: _check_submitter_eligibility(submitter, assg_name, submission_dir),
              Stage.COMPILE: lambda: _compile_submission(submitter),
              Stage.VALIDATE_TESTS: lambda: _validate_tests(submitter),
              Stage.VALIDATE_PROGS: lambda: _validate_programs_under_test(submitter),
              Stage.SUBMIT: lambda: _submit(submitter)
              }.get(stage, lambda: Result(False, "Stage {} not implemented".format(stage.name)))()

    # process the results
    if result:
        if stage != Stage.SUBMIT:
            # Update the prev_stage flag so that the next stage can be run
            # No need to do so for SUBMIT as it is the final stage
            clear_all_flags(pre_val_dir)
            set_flag(stage.value, True, pre_val_dir)
    else:
        print_tourney_trace("Submission from {} rejected. Did not pass the {} stage".format(submitter, stage))
        if stage != Stage.CHECK_ELIG:
            # Don't remove a submission in the pre_val dir if stage == CHECK_ELIG.
            # This stage may fail due to a prior submission still being processed and we don't want to delete that
            subprocess.run("rm -rf {}".format(pre_val_dir), shell=True)

    return result


def _submission_details(submitter: Submitter) -> (Submitter, FilePath, AbstractAssignment):
    """ Get important details for a submitter given their username """
    _, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    submitter_pre_validation_dir = paths.get_pre_validation_dir(submitter_username)
    assg = AssignmentConfig().get_assignment()

    return submitter_username, submitter_pre_validation_dir, assg


def _check_submitter_eligibility(submitter: Submitter, assg_name: str, submission_dir: FilePath) -> Result:
    """
    Check that the submitter has made a submission that is eligible for the tournament.
    :param submitter: The name of the submitter
    :param assg_name: The name of the assignment submitted
    :param submission_dir: The location of the submission prior to moving into the pre_validation directory
    :return: Whether the submitter is eligible, with traces
    """

    daemon_online = daemon.is_alive()
    if not daemon_online:
        return daemon_online

    _, submitter_pre_val_dir, assg = _submission_details(submitter)

    if assg_name != assg.get_assignment_name():
        return Result(False, "Error: The submitted assignment '{}' does not match the assignment "
                             "this tournament is configured for: '{}'".format(assg_name, assg.get_assignment_name()))

    submitter_eligible, _ = ApprovedSubmitters().get_submitter_username(submitter)
    if not submitter_eligible:
        return Result(False, "Submitter '{}' is not on the approved submitters list.\n"
                             "If this is a group assignment please check that you are committing to "
                             "the repo of your designated team representative.\n"
                             "If this is an individual assignment please check with your tutors that"
                             " you are added to the approved_submitters list".format(submitter))

    if os.path.isdir(submitter_pre_val_dir):
        prior_submission_age = datetime.now().timestamp() - os.stat(submitter_pre_val_dir).st_mtime
        stale_submission_age = 60 * 15  # 15 minutes, a prior submission older than this can be discarded
        if prior_submission_age < stale_submission_age:
            return Result(False, "Error: A prior submission is still being validated. "
                                 "Please wait {} seconds to push a new commit."
                          .format(int(stale_submission_age - prior_submission_age)))

    # if submitter is eligible then move submission into the pre_validation folder and prepare for validation
    subprocess.run("cp -rf {} {}".format(assg.get_source_assg_dir(), submitter_pre_val_dir), shell=True)
    result = assg.prep_submission(FilePath(submission_dir), FilePath(submitter_pre_val_dir))

    if not result:
        return Result(False, "An error occurred while preparing the submission:\n{}".format(result.traces))

    return Result(True, "Submitter is eligible for the tournament")


def _compile_submission(submitter: Submitter) -> Result:
    """
    Compile any tests or programs under test in a submission, if necessary.
    :param submitter: The name of the submitter
    :return: Whether compilation was successful
    """

    _, submitter_pre_val_dir, assg = _submission_details(submitter)

    # compile progs under test
    result = Result(True, "Compiling programs:")
    for prog in ["original"] + assg.get_programs_list():
        compil_result = assg.compile_prog(submitter_pre_val_dir, prog)

        result.traces += "\n\t{} compilation ".format(prog)
        result.traces += "SUCCESS" if compil_result else ("FAILED.\n" + compil_result.traces)
        result.success = result.success and compil_result.success

    # compile tests
    result.traces += "\n\nCompiling tests:"
    for test in assg.get_test_list():
        compil_result = assg.compile_test(submitter_pre_val_dir, test)

        result.traces += "\n\t{} compilation ".format(test)
        result.traces += "SUCCESS" if compil_result else ("FAILED.\n" + compil_result.traces)
        result.success = result.success and compil_result.success

    return result


def _validate_tests(submitter: Submitter) -> Result:
    """
    Validate that all tests provided by a submitter correctly detect no errors in the original assignment code.
    :param submitter: the submitter whose tests are to be validated
    :return: Whether the tests are valid, with traces
    """
    # The submission has been placed in the prevalidation dir as a result of running check_submitter_eligibility first
    _, submitter_pre_val_dir, assg = _submission_details(submitter)

    if not os.path.exists(submitter_pre_val_dir):
        return Result(False, "Student submission not found in the `pre_validation` folder.\n"
                             "This can be caused by manually retrying a failed test stage via the gitlab web "
                             "interface. In order to do so you will need to manually re-run all stages in order "
                             "(including stages that have previously passed).\n"
                             "However, the recommended approach is to push a new commit which will run the entire "
                             "test pipeline")

    assg = AssignmentConfig().get_assignment()

    num_tests = {}
    tests_valid = True
    validation_traces = "Validation results:"
    for test in assg.get_test_list():
        test_result, test_traces = assg.run_test(test, Prog("original"), FilePath(submitter_pre_val_dir))

        validation_traces += "\n\t{} test ".format(test)
        validation_traces += \
            {TestResult.TIMEOUT: "FAIL    - Timeout when run against original program: {}".format(test_traces),
             TestResult.NO_BUGS_DETECTED: "SUCCESS - No bugs detected in original program",
             TestResult.BUG_FOUND: "FAIL    - Test falsely reports error in original code\n" + test_traces,
             TestResult.UNEXPECTED_RETURN_CODE: "FAIL    - Unrecognised return code found\n" + test_traces
             }.get(test_result, "ERROR   - unexpected test result: {}".format(test_result))

        tests_valid = tests_valid and test_result == TestResult.NO_BUGS_DETECTED
        if tests_valid:
            num_tests[test] = assg.get_num_tests(test_traces)

    if tests_valid:
        json.dump(num_tests, open(submitter_pre_val_dir + "/" + paths.NUM_TESTS_FILE, 'w'))

    return Result(tests_valid, validation_traces)


def _validate_programs_under_test(submitter: Submitter) -> Result:
    """
    Validate that all programs provided by a submitter have bugs detected by the submitters own test suites.
    :param submitter: the submitter whose programs are to be validated
    :return: Whether the programs are valid, with traces
    """
    # The submission has been placed in the prevalidation dir as a result of running check_submitter_eligibility first
    _, submitter_pre_val_dir, assg = _submission_details(submitter)

    if not os.path.exists(submitter_pre_val_dir):
        return Result(False, "Student submission not found in the `pre_validation` folder.\n"
                             "This can be caused by manually retrying a failed test stage via the gitlab web "
                             "interface. In order to do so you will need to manually re-run all stages in order "
                             "(including stages that have previously passed).\n"
                             "However, the recommended approach is to push a new commit which will run the entire "
                             "test pipeline")

    assg = AssignmentConfig().get_assignment()

    progs_valid = True
    validation_traces = "Validation results:"
    for prog in assg.get_programs_list():

        other_progs = takewhile(lambda p, curr_prog=prog: p != curr_prog, assg.get_programs_list())
        duplicate_progs = [other for other in other_progs if assg.progs_identical(prog, other, submitter_pre_val_dir)]

        if duplicate_progs:
            validation_traces += "\n\t{} FAIL - Duplicate of {}".format(prog, duplicate_progs[0])
            progs_valid = False
            continue

        for test in assg.get_test_list():
            test_result, test_traces = assg.run_test(test, prog, FilePath(submitter_pre_val_dir), use_poc=True)

            validation_traces += "\n\t{} {} test ".format(prog, test)
            validation_traces += \
                {TestResult.TIMEOUT: "FAIL    - Timeout",
                 TestResult.NO_BUGS_DETECTED: "FAIL    - Test suite does not detect error",
                 TestResult.BUG_FOUND: "SUCCESS - Test suite detects error",
                 TestResult.UNEXPECTED_RETURN_CODE: "FAIL    - Unrecognised return code found\n" + test_traces,
                 }.get(test_result, "ERROR   - unexpected test result: {}".format(test_result))

            progs_valid = progs_valid and test_result == TestResult.BUG_FOUND

    return Result(progs_valid, validation_traces)


def _check_submission_file_size(pre_val_dir: FilePath) -> Result:
    """ Check that the size of the submissions is not too large """
    result = subprocess.run("du -sh {}".format(pre_val_dir),
                            stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    filesize_pattern = "^([0-9]+(?:\\.[0-9]+)?)([BKMG])"  # number and scale, eg: "744K" = 744KB or "1.8G" == 1.8GB
    submission_size_regex = re.search(filesize_pattern, result.stdout)

    if submission_size_regex is not None:
        size_in_bytes = float(submission_size_regex.group(1)) * \
                        {"B": 1, "K": 1000, "M": 1000000, "G": 1000000000}.get(submission_size_regex.group(2))
        if size_in_bytes > 150 * 1000 * 1000:  # 150 MB
            error_string = "Error: After compilation and test generation the submission file size ({}) is larger than "\
                           "150 megabytes.\nServer space is limited so please keep your submissions to a " \
                           "reasonable size\n".format("".join(submission_size_regex.groups()))
            error_string += "Further details:\n{}".format(
                subprocess.run("du -d 2 -h .", cwd=pre_val_dir, shell=True, universal_newlines=True,
                               stdout=subprocess.PIPE).stdout)

            return Result(False, error_string)
    return Result(True, "submission size valid")


def _submit(submitter: Submitter) -> Result:
    """ Create a submission for a submitter in the paths.STAGED_DIR """

    pre_val_dir = paths.get_pre_validation_dir(submitter)
    submission_time = datetime.now()

    if ApprovedSubmitters().submissions_closed() and not SubmitterExtensions().is_eligible(submitter):
        return Result(False, "A new submission cannot be made at {}. Submissions have been closed"
                      .format(submission_time.strftime(fmt.DATETIME_TRACE_STRING)))

    size_check_result = _check_submission_file_size(pre_val_dir)
    if not size_check_result:
        return size_check_result

    return daemon.queue_submission(submitter, submission_time)
