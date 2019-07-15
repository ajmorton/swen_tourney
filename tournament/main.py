from typing import Tuple, Dict
from tournament.util.types.tourney_state import TourneyState
from tournament.util.types.basetypes import TestResult
import tournament.config.paths as paths
import tournament.config.config as config


assg = config.assignment


def check_submitter_eligibility(submitter: str) -> bool:
    return submitter in open(paths.SUBMITTERS_LIST).read()


def validate_tests(submission_dir: str) -> Tuple[bool, str]:
    assg.prep_submission(submission_dir)

    tests_valid = True
    validation_traces = "Validation results:"
    for test in assg.get_test_list():
        test_result = assg.run_test(test, "original", submission_dir)

        if test_result == TestResult.TIMEOUT:
            validation_traces += "\n{} {} test FAIL - Timeout".format("original", test)
        elif test_result == TestResult.TEST_PASSED:
            validation_traces += "\n{} {} test SUCCESS - No bugs detected in original program".format("original", test)
        elif test_result == TestResult.TEST_FAILED:
            validation_traces += "\n{} {} test FAIL - Test falsely reports an error in original code".format("original", test)
        else:
            validation_traces += "\n{} {} ERROR - unexpected test result: {}".format("original", test, test_result)

        tests_valid = tests_valid and test_result == TestResult.TEST_PASSED

    return tests_valid, validation_traces


def validate_programs_under_test(submission_dir: str) -> Tuple[bool, str]:
    assg.prep_submission(submission_dir)

    progs_valid = True
    validation_traces = "Validation results:"

    for prog in assg.get_programs_under_test_list():
        for test in assg.get_test_list():
            test_result = assg.run_test(test, prog, submission_dir)

            if test_result == TestResult.TIMEOUT:
                validation_traces += "\n{} {} test FAIL - Timeout".format(prog, test)
            elif test_result == TestResult.TEST_PASSED:
                validation_traces += "\n{} {} test FAIL - Test suite does not detect error".format(prog, test)
            elif test_result == TestResult.TEST_FAILED:
                validation_traces += "\n{} {} test SUCCESS - Test suite detects error".format(prog, test)
            else:
                validation_traces += "\n{} {} ERROR - unexpected test result: {}".format(prog, test, test_result)

            progs_valid = progs_valid and test_result == TestResult.TEST_FAILED

    return progs_valid, validation_traces


def run_submission(submitter: str):

    # TODO No need to read on every submission? Needs to tie in with check_submitter_eligibility above
    tourney_state = TourneyState()
    other_submitters = [sub for sub in tourney_state.get_valid_submitters() if sub != submitter]

    # run submitter tests against others progs
    testing_results = run_tests([submitter], other_submitters)

    # run others tests against submitters progs
    proging_results = run_tests(other_submitters, [submitter])

    for (tester, progr) in testing_results.keys():
        tourney_state.set(tester, progr, testing_results[(tester, progr)])

    for (tester, progr) in proging_results.keys():
        tourney_state.set(tester, progr, proging_results[(tester, progr)])

    tourney_state.print()
    tourney_state.save_to_file()


def rand_result() -> TestResult:
    import random
    num = random.randint(1, 3)

    if num == 1:
        return TestResult.TEST_PASSED
    elif num == 2:
        return TestResult.TEST_FAILED
    else:
        return TestResult.TIMEOUT


def run_tests(testers: [str], progrs: [str]) -> [Dict[str, Dict[str, str]]]:

    #TODO threading
    staging_dir = paths.HEAD_TO_HEAD_DIR

    all_results = {}

    for tester in testers:
        for progr in progrs:
            #TODO
            # prepare testing stage for (symlinks)
            test_set = {}
            for test in assg.get_test_list():
                test_set[test] = {}
                for prog in assg.get_programs_under_test_list():
                    test_set[test][prog] = rand_result()

            all_results[(tester, progr)] = test_set

    return all_results
