import subprocess
import os
import multiprocessing
from functools import partial
from tournament.state.tourney_state import TourneyState
from util import paths
from config.configuration import ApprovedSubmitters, AssignmentConfig
from util.types import *
from util.funcs import print_tourney_trace
from daemon import flags
from datetime import datetime
from util import format as fmt
import json


def check_submitter_eligibility(submitter: Submitter, assg_name: str, submission_dir: FilePath) -> Result:

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
                              .format(datetime.now().strftime(fmt.datetime_trace_string))))

    # if submitter is eligible then move submission into the pre_validation folder and prepare for validation
    submitter_pre_validation_dir = paths.get_pre_validation_dir(submitter_username)
    if os.path.isdir(submitter_pre_validation_dir):
        return Result((False, "Error: A prior submission is still being validated. "
                              "Please wait until it has finished to push a new commit."))

    subprocess.run(
        "cp -rf {} {}".format(assg.get_source_assg_dir(), submitter_pre_validation_dir),
        shell=True
    )

    assg.prep_submission(FilePath(submission_dir), FilePath(submitter_pre_validation_dir))

    return Result((True, "Submitter is eligible for the tournament"))


def validate_tests(submitter: Submitter) -> Result:
    _, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    validation_dir = paths.get_pre_validation_dir(submitter_username)
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
    _, submitter_username = ApprovedSubmitters().get_submitter_username(submitter)
    validation_dir = paths.get_pre_validation_dir(submitter_username)
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

    with multiprocessing.Pool() as p:
        # run submitter tests against others progs
        tester_pairs = [(submitter, other) for other in other_submitters]
        tester_results = p.map(rt_new_tests, tester_pairs)

        # run others tests against submitters progs
        testee_pairs = [(other, submitter) for other in other_submitters]
        testee_results = p.map(rt_new_progs, testee_pairs)

    for (tester, testee, test_set) in tester_results + testee_results:
        tourney_state.set(tester, testee, test_set)

    print_tourney_trace("Submission from {} tested".format(submitter))
    tourney_state.save_to_file()


def run_tests(pair: Tuple[Submitter, Submitter], tourney_state: TourneyState, new_tests: [Test], new_progs: [Prog]
              ) -> [Submitter, Submitter, TestSet]:

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
    flags.clear_all()

