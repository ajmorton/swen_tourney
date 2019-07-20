from typing import Tuple
import subprocess
from datetime import datetime
import os
import json
import multiprocessing
from functools import partial
from tournament.util.types.tourney_state import TourneyState
import tournament.config.paths as paths
import tournament.config.config as config
from tournament.util.types.basetypes import *


assg = config.assignment


def check_submitter_eligibility(submitter: Submitter, submission_dir: FilePath) -> Tuple[bool, str]:
    submitter_eligible = submitter in open(paths.SUBMITTERS_LIST).read()
    assg_folder = os.path.basename(assg.get_source_assg_dir().rstrip("/"))

    if submitter_eligible:
        # if submitter is eligible then move submission into the pre_validation folder and prepare for validation
        submitter_pre_validation_dir = paths.PRE_VALIDATION_DIR + "/" + submitter
        if os.path.isdir(submitter_pre_validation_dir):
            subprocess.run("rm -rf {}".format(submitter_pre_validation_dir), shell=True)
        subprocess.run("mkdir {}".format(submitter_pre_validation_dir), shell=True)

        subprocess.run(
            "cp -rf {} {}".format(assg.get_source_assg_dir(), submitter_pre_validation_dir + "/" + assg_folder),
            shell=True
        )
        assg.prep_submission(submission_dir, submitter_pre_validation_dir)

    if submitter_eligible:
        eligibility_check_traces = "Submitter is eligible for the tournament"
    else:
        eligibility_check_traces = \
            "Submitter '{}' is not on the approved submitters list.\n"\
            "If this is a group assignment please check that you are committing to "\
            "the repo of your designated team representative.\n"\
            "If this is an individual assignment please check with your tutors that"\
            " you are added to the approved_submitters list".format(submitter)

    return submitter_eligible, eligibility_check_traces


def validate_tests(submitter: Submitter) -> Tuple[bool, str]:
    validation_dir = paths.PRE_VALIDATION_DIR + "/" + submitter

    tests_valid = True
    validation_traces = "Validation results:"
    for test in assg.get_test_list():
        test_result = assg.run_test(test, "original", validation_dir)

        if test_result == TestResult.TIMEOUT:
            validation_traces += "\n{} {} test FAIL - Timeout".format("original", test)
        elif test_result == TestResult.NO_BUGS_DETECTED:
            validation_traces += "\n{} {} test SUCCESS - No bugs detected in original program".format("original", test)
        elif test_result == TestResult.BUG_FOUND:
            validation_traces += \
                "\n{} {} test FAIL - Test falsely reports an error in original code".format("original", test)
        else:
            validation_traces += "\n{} {} ERROR - unexpected test result: {}".format("original", test, test_result)

        tests_valid = tests_valid and test_result == TestResult.NO_BUGS_DETECTED

    return tests_valid, validation_traces


def validate_programs_under_test(submitter: Submitter) -> Tuple[bool, str]:
    validation_dir = paths.PRE_VALIDATION_DIR + "/" + submitter

    progs_valid = True
    validation_traces = "Validation results:"

    for prog in assg.get_programs_list():
        for test in assg.get_test_list():
            test_result = assg.run_test(test, prog, validation_dir)

            if test_result == TestResult.TIMEOUT:
                validation_traces += "\n{} {} test FAIL - Timeout".format(prog, test)
            elif test_result == TestResult.NO_BUGS_DETECTED:
                validation_traces += "\n{} {} test FAIL - Test suite does not detect error".format(prog, test)
            elif test_result == TestResult.BUG_FOUND:
                validation_traces += "\n{} {} test SUCCESS - Test suite detects error".format(prog, test)
            else:
                validation_traces += "\n{} {} ERROR - unexpected test result: {}".format(prog, test, test_result)

            progs_valid = progs_valid and test_result == TestResult.BUG_FOUND

    return progs_valid, validation_traces


def detect_new_tests(submitter: Submitter):
    new_submission_dir = paths.PRE_VALIDATION_DIR + "/" + submitter
    previous_submission_dir = paths.TOURNEY_DIR + "/" + submitter

    new_tests = assg.detect_new_tests(new_submission_dir, previous_submission_dir)
    new_tests_file_path = new_submission_dir + "/" + paths.NEW_TESTS_FILE

    new_tests_file = open(new_tests_file_path, "w")
    json.dump(new_tests, new_tests_file)


def detect_new_progs(submitter: Submitter):
    new_submission_dir = paths.PRE_VALIDATION_DIR + "/" + submitter
    previous_submission_dir = paths.TOURNEY_DIR + "/" + submitter

    new_progs = assg.detect_new_progs(new_submission_dir, previous_submission_dir)
    new_progs_file_path = new_submission_dir + "/" + paths.NEW_PROGS_FILE

    new_tests_file = open(new_progs_file_path, "w")
    json.dump(new_progs, new_tests_file)


def run_submission(submitter: Submitter):

    # TODO No need to read on every submission? Needs to tie in with check_submitter_eligibility above
    tourney_state = TourneyState()
    other_submitters = [sub for sub in tourney_state.get_valid_submitters() if sub != submitter]

    new_tests_file = paths.TOURNEY_DIR + "/" + submitter + "/" + paths.NEW_TESTS_FILE
    new_tests = json.load(open(new_tests_file, "r"))

    new_progs_file = paths.TOURNEY_DIR + "/" + submitter + "/" + paths.NEW_PROGS_FILE
    new_progs = json.load(open(new_progs_file, "r"))

    print("Processing submission for {}.".format(submitter))
    print("New tests: {}".format(new_tests))
    print("New progs: {}".format(new_progs))

    # multiprocessing.Pool.map can only work on one argument, use functools.partial to curry
    # run_tests into a function with just one argument
    rt = partial(run_tests, new_tests=new_tests, new_progs=new_progs, tourney_state=tourney_state)

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        # run submitter tests against others progs
        tester_pairs = [(submitter, other) for other in other_submitters]
        tester_results = p.map(rt, tester_pairs)

        # run others tests against submitters progs
        testee_pairs = [(other, submitter) for other in other_submitters]
        testee_results = p.map(rt, testee_pairs)

    for (tester, testee, test_set) in tester_results + testee_results:
        tourney_state.set(tester, testee, test_set)

    print("Submission from {} tested".format(submitter))
    tourney_state.save_to_file()


def run_tests(
        pair: Tuple[Submitter, Submitter],
        tourney_state: TourneyState,
        new_tests: [Test] = assg.get_test_list(),
        new_progs: [Prog] = assg.get_programs_list()
) -> [Submitter, Submitter, TestSet]:
    test_stage_dir = paths.HEAD_TO_HEAD_DIR + "/test_stage_" + multiprocessing.current_process().name
    if not os.path.isdir(test_stage_dir):
        subprocess.run("mkdir {}".format(test_stage_dir), shell=True)
        subprocess.run("cp -rf {} {}".format(assg.get_source_assg_dir(), test_stage_dir), shell=True)

    (tester, testee) = pair

    assg.prep_test_stage(tester, testee, test_stage_dir)
    test_set = {}
    for test in assg.get_test_list():
        test_set[test] = {}
        for prog in assg.get_programs_list():
            if test not in new_tests and prog not in new_progs:
                # no need to rerun this test, keep the results from the current tournament state
                test_set[test][prog] = tourney_state.get(tester, testee, test, prog)
            else:
                test_set[test][prog] = assg.run_test(test, prog, test_stage_dir)

    return tester, testee, test_set


def generate_report(time: datetime):
    tourney_state = TourneyState()
    report = {
        'datetime': time.isoformat(),
        'result': tourney_state.get_results()
    }

    report_file_path = paths.REPORT_DIR + "/report_" + time.strftime("%Y_%m_%d-%H:%M") + ".json"

    with open(report_file_path, 'w') as outfile:
        json.dump(report, outfile, indent=4)

    print("Report written to {}".format(report_file_path))


def clean():
    """
    Remove all submissions and reset the tourney state
    """
    subprocess.run("rm -rf {}".format(paths.PRE_VALIDATION_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.STAGING_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.TOURNEY_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.HEAD_TO_HEAD_DIR + "/*"), shell=True)
    subprocess.run("rm -f  {}".format(paths.TOURNEY_STATE_FILE), shell=True)
