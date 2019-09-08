"""
The core functions used for running the tournament
"""
import csv
import json
import multiprocessing
import os
import subprocess
from datetime import datetime
from functools import partial
from typing import Tuple

from config.configuration import ApprovedSubmitters, AssignmentConfig
from daemon import flags
from tournament.state.tourney_snapshot import TourneySnapshot
from tournament.state.tourney_state import TourneyState
from util import format as fmt
from util import paths
from util.funcs import print_tourney_trace
from util.types import FilePath, Prog, Result, Submitter, Test, TestResult, TestSet


def check_submitter_eligibility(submitter: Submitter, assg_name: str, submission_dir: FilePath) -> Result:
    """
    Check that the submitter has made a submission that is eligible for the tournament.
    :param submitter: The name of the submitter
    :param assg_name: The name of the assignment submitted
    :param submission_dir: the directory of the submission
    :return: Whether the submitter is eligible, with traces
    """

    if not flags.get_flag(flags.Flag.ALIVE):
        return Result((False, "Error: The tournament is not currently online."))

    assg = AssignmentConfig().get_assignment()
    if assg_name != assg.get_assignment_name():
        return Result((False, "Error: The submitted assignment '{}' does not match the assignment "
                              "the tournament is configured for: '{}'".format(assg_name, assg.get_assignment_name())))

    submitter_eligible, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    if not submitter_eligible:
        return Result((False, "Submitter '{}' is not on the approved submitters list.\n"
                              "If this is a group assignment please check that you are committing to "
                              "the repo of your designated team representative.\n"
                              "If this is an individual assignment please check with your tutors that"
                              " you are added to the approved_submitters list".format(submitter)))

    submissions_closed = flags.get_flag(flags.Flag.SUBMISSIONS_CLOSED)
    if submissions_closed:
        return Result((False, "Cannot make a new submission at {}. Submissions have been closed"
                       .format(datetime.now().strftime(fmt.DATETIME_TRACE_STRING))))

    submitter_pre_validation_dir = paths.get_pre_validation_dir(submitter_username)
    if os.path.isdir(submitter_pre_validation_dir):
        prior_submission_age = datetime.now().timestamp() - os.stat(submitter_pre_validation_dir).st_mtime
        stale_submission_age = 60 * 15  # 15 minutes, a prior submission older than this can be discarded
        if prior_submission_age < stale_submission_age:
            return Result((False, "Error: A prior submission is still being validated. "
                                  "Please wait until it has finished to push a new commit."))

    # if submitter is eligible then move submission into the pre_validation folder and prepare for validation
    subprocess.run(
        "cp -rf {} {}".format(assg.get_source_assg_dir(), submitter_pre_validation_dir),
        shell=True
    )

    assg.prep_submission(FilePath(submission_dir), FilePath(submitter_pre_validation_dir))

    return Result((True, "Submitter is eligible for the tournament"))


def validate_tests(submitter: Submitter) -> Result:
    """
    Validate that all tests provided by a submitter correctly detect no errors in the original assignment code.
    :param submitter: the submitter whose tests are to be validated
    :return: Whether the tests are valid, with traces
    """
    # The submission has been placed in the prevalidation dir as a result of running check_submitter_eligibility first
    _, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    validation_dir = paths.get_pre_validation_dir(submitter_username)

    if not os.path.exists(validation_dir):
        return Result((False, "Student submission not found in the `pre_validation` folder.\n"
                              "This can be caused by manually retrying a failed test stage via the gitlab web "
                              "interface. In order to do so you will need to manually re-run all stages in order "
                              "(including stages that have previously passed).\n"
                              "However, the recommended approach is to push a new commit which will run the entire "
                              "test pipeline"))

    assg = AssignmentConfig().get_assignment()

    num_tests = {}
    tests_valid = True
    validation_traces = "Validation results:"
    for test in assg.get_test_list():
        test_result, test_traces = assg.run_test(test, Prog("original"), FilePath(validation_dir))

        if test_result == TestResult.TIMEOUT:
            validation_traces += "\n\t{} test FAIL - Timeout".format(test)
        elif test_result == TestResult.NO_BUGS_DETECTED:
            validation_traces += "\n\t{} test SUCCESS - No bugs detected in original program".format(test)
        elif test_result == TestResult.BUG_FOUND:
            validation_traces += "\n{} test FAIL - Test falsely reports an error in original code".format(test)
            validation_traces += "\n" + test_traces
        else:
            validation_traces += "\n\t{} ERROR - unexpected test result: {}".format(test, test_result)

        tests_valid = tests_valid and test_result == TestResult.NO_BUGS_DETECTED
        if tests_valid:
            num_tests[test] = assg.get_num_tests(test_traces)

    if not tests_valid:
        subprocess.run("rm -rf {}".format(validation_dir), shell=True)
    else:
        json.dump(num_tests, open(validation_dir + "/" + paths.NUM_TESTS_FILE, 'w'))

    return Result((tests_valid, validation_traces))


def validate_programs_under_test(submitter: Submitter) -> Result:
    """
    Validate that all programs provided by a submitter have bugs detected by the submitters own test suites.
    :param submitter: the submitter whose programs are to be validated
    :return: Whether the programs are valid, with traces
    """
    # The submission has been placed in the prevalidation dir as a result of running check_submitter_eligibility first
    _, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    validation_dir = paths.get_pre_validation_dir(submitter_username)
    if not os.path.exists(validation_dir):
        return Result((False, "Student submission not found in the `pre_validation` folder.\n"
                              "This can be caused by manually retrying a failed test stage via the gitlab web "
                              "interface. In order to do so you will need to manually re-run all stages in order "
                              "(including stages that have previously passed).\n"
                              "However, the recommended approach is to push a new commit which will run the entire "
                              "test pipeline"))

    assg = AssignmentConfig().get_assignment()

    progs_valid = True
    validation_traces = "Validation results:"
    for prog in assg.get_programs_list():
        for test in assg.get_test_list():
            test_result, _ = assg.run_test(test, prog, FilePath(validation_dir))

            if test_result == TestResult.TIMEOUT:
                validation_traces += "\n\t{} {} test FAIL - Timeout".format(prog, test)
            elif test_result == TestResult.NO_BUGS_DETECTED:
                validation_traces += "\n\t{} {} test FAIL - Test suite does not detect error".format(prog, test)
            elif test_result == TestResult.BUG_FOUND:
                validation_traces += "\n\t{} {} test SUCCESS - Test suite detects error".format(prog, test)
            else:
                validation_traces += "\n\t{} {} ERROR - unexpected test result: {}".format(prog, test, test_result)

            progs_valid = progs_valid and test_result == TestResult.BUG_FOUND

    if not progs_valid:
        subprocess.run("rm -rf {}".format(validation_dir), shell=True)

    return Result((progs_valid, validation_traces))


def run_submission(submitter: Submitter, submission_time: str, new_tests: [Test], new_progs: [Prog]):
    """
    Run a submission against all other previously made submissions in the tournament.
    The submission has been compared against the submitters prior submission (if any). Only new tests and progs require
    retesting
    :param submitter: the submitter
    :param submission_time: the time of the new submission
    :param new_tests: the list of new tests that need to be run/rerun
    :param new_progs: the list of new programs that need to be run/rerun
    """

    tourney_state = TourneyState()
    other_submitters = [sub for sub in tourney_state.get_valid_submitters() if sub != submitter]

    print_tourney_trace("Processing submission for {}.".format(submitter))
    print_tourney_trace("\tNew tests: {}".format(new_tests))
    print_tourney_trace("\tNew progs: {}".format(new_progs))

    tourney_state.set_time_of_submission(submitter, submission_time)
    num_tests = json.load(open(paths.get_tourney_dir(submitter) + "/" + paths.NUM_TESTS_FILE, 'r'))
    tourney_state.set_number_of_tests(submitter, num_tests)

    # run_tests will create staging directories for testing based on the thread id.
    # As multiprocessing.pool allocates incrementing thread ids this leads to an increasing number of staging dirs,
    # and in turn a memory leak of sorts.
    # Instead, make sure that the head_to_head dir is empty before running to prevent this.
    subprocess.run("rm -rf {}".format(paths.HEAD_TO_HEAD_DIR + "/*"), shell=True)

    # multiprocessing.Pool.map can only work on one argument, use functools.partial to curry
    # run_tests into functions with just one argument
    rt_new_tests = partial(run_tests, tourney_state=tourney_state, new_tests=new_tests, new_progs=[])
    rt_new_progs = partial(run_tests, tourney_state=tourney_state, new_tests=[], new_progs=new_progs)

    with multiprocessing.Pool() as pool:
        # run submitter tests against others progs
        tester_results = pool.map(rt_new_tests, [(submitter, other) for other in other_submitters])

        # run others tests against submitters progs
        testee_results = pool.map(rt_new_progs, [(other, submitter) for other in other_submitters])

    for (tester, testee, test_set) in tester_results + testee_results:
        tourney_state.set(tester, testee, test_set)

    print_tourney_trace("Submission from {} tested".format(submitter))
    tourney_state.save_to_file()


def run_tests(pair: Tuple[Submitter, Submitter], tourney_state: TourneyState, new_tests: [Test], new_progs: [Prog]
              ) -> [Submitter, Submitter, TestSet]:
    """
    Provided a tester/testee pair, run the testers tests against the testees programs.
    If a test or a program is marked as new then run the test against the program, otherwise the values can be taken
    from the existing tournament state
    :param pair: the tester/testee pair
    :param tourney_state: the existing tournament state
    :param new_tests: the list of new tests that need to be run
    :param new_progs: the list of new programs that need to be tested
    :return: (tester, testee, results of running all tests against all programs)
    """

    assg = AssignmentConfig().get_assignment()

    test_stage_dir = paths.HEAD_TO_HEAD_DIR + "/test_stage_" + multiprocessing.current_process().name
    if not os.path.isdir(test_stage_dir):
        subprocess.run("cp -rf {} {}".format(assg.get_source_assg_dir(), test_stage_dir), shell=True)

    (tester, testee) = pair

    assg.prep_test_stage(tester, testee, test_stage_dir)
    test_set = {}
    for test in assg.get_test_list():
        test_set[test] = {}
        for prog in assg.get_programs_list():
            if test in new_tests or prog in new_progs:
                test_set[test][prog], _ = assg.run_test(test, prog, test_stage_dir)
            else:
                # no need to rerun this test, keep the results from the current tournament state
                test_set[test][prog] = tourney_state.get(tester, testee, test, prog)

    return tester, testee, test_set


def get_diffs() -> Result:
    """
    Print to paths.DIFF_FILE the changes each submitter made in their programs compared to the original program.
    """

    if not flags.get_flag(flags.Flag.SUBMISSIONS_CLOSED):
        return Result((False, "Submissions are not currently closed.\n "
                              "get_diffs should only be called once submissions are closed"))

    assg = AssignmentConfig().get_assignment()
    tourney_results = json.load(open(paths.RESULTS_FILE, 'r'))

    csv_columns = ["submitter", "mutant", "num_tests_evaded", "diff", "invalid?"]
    diff_csv = csv.DictWriter(open(paths.DIFF_FILE, 'w'), fieldnames=csv_columns)
    diff_csv.writeheader()

    diffs = []
    for submitter in os.listdir(paths.TOURNEY_DIR):
        print("diffing {}".format(submitter))
        submitter_diffs = assg.get_diffs(paths.get_tourney_dir(Submitter(submitter)))
        for prog in sorted(submitter_diffs.keys()):
            num_tests_evaded = tourney_results['results'][submitter]['progs'][prog]
            diffs.append({'submitter': submitter, 'mutant': prog, 'num_tests_evaded': num_tests_evaded,
                          'diff': submitter_diffs[prog], 'invalid?': ""})

    # sort by num_tests_evaded, the most successful programs will be at the top of the csv file and
    # are prioritised for inspection
    for entry in sorted(diffs, key=lambda e: e['num_tests_evaded'], reverse=True):
        diff_csv.writerow(entry)

    invalid = ["Y", "y", "True", "true", "X", "x"]
    valid = ["N", "n", ""]

    return Result((True, "\nDiff file has been created at: {}.\n"
                         "Invalid entries should be marked with one of {} in the 'invalid?' column, "
                         "valid entries can be marked with one of {}."
                   .format(paths.DIFF_FILE, invalid, valid)))


def rescore_invalid_progs() -> Result:
    """
    Read from the diff file which submitted progs are invalid, and give those programs a score of zero in
    the tournament state
    """

    if not flags.get_flag(flags.Flag.SUBMISSIONS_CLOSED):
        return Result((False, "Submissions are not currently closed.\n "
                              "Rescoring invalid programs should only be performed once submissions are closed"))

    if not os.path.exists(paths.DIFF_FILE):
        return Result((False, "Error the diff file '{}' does not exist.\n"
                              "Make sure to run 'get_diffs' and update the resulting file before running "
                              "this command.".format(paths.DIFF_FILE)))

    diff_csv = csv.DictReader(open(paths.DIFF_FILE, 'r'))
    tourney_state = TourneyState()

    invalid = ["Y", "y", "True", "true", "X", "x"]
    valid = ["N", "n", ""]

    num_invalid_progs = 0
    unrecognised_value = False
    for row in diff_csv:
        is_invalid, sub, mut = row['invalid?'], row['submitter'], row['mutant']
        if is_invalid in invalid:
            tourney_state.invalidate_prog(sub, mut)
            num_invalid_progs += 1
        elif is_invalid in valid:
            continue
        else:
            unrecognised_value = True
            print("Error: unrecognised value '{}' in the 'invalid?' column for {} {}."
                  .format(is_invalid, sub, mut))

    if unrecognised_value:
        print("\nUnrecognised values in the 'invalid?' column of {} have been detected. "
              "Please use one of {} for valid entries, or one of {} for invalid entries"
              .format(paths.DIFF_FILE, valid, invalid))

    # update tourney state and results
    print("\nResults updated. Recalculating submitter scores.")
    tourney_state.save_to_file()
    TourneySnapshot(report_time=datetime.now()).write_snapshot()

    return Result((True, "{} invalid programs have had their score set to zero".format(num_invalid_progs)))


def clean():
    """
    Remove all submissions and reset the tourney state
    """
    subprocess.run("rm -rf {}".format(paths.PRE_VALIDATION_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.STAGING_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.TOURNEY_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.HEAD_TO_HEAD_DIR + "/*"), shell=True)
    subprocess.run("rm -f  {}".format(paths.TOURNEY_STATE_FILE), shell=True)
    subprocess.run("rm -f  {}".format(paths.TRACE_FILE), shell=True)
    subprocess.run("rm -f  {}".format(paths.RESULTS_FILE), shell=True)
    subprocess.run("rm -f  {}/snapshot*.json".format(paths.REPORT_DIR), shell=True)
    subprocess.run("rm -f  {}".format(paths.ASSIGNMENT_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.APPROVED_SUBMITTERS_LIST), shell=True)
    subprocess.run("rm -f  {}".format(paths.SERVER_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.EMAIL_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.DIFF_FILE), shell=True)
    flags.clear_all()
