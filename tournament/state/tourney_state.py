import json
import os

from config.configuration import ApprovedSubmitters, AssignmentConfig
from util import paths
from util.types import *


class TourneyState:
    """
    Maintain a record of which students tests have detected or missed which student's bugged progs.
    This can be saved and loaded from a json file to help mitigate crashes.
    """

    def __init__(self):
        self.state = {}

        approved_submitters = ApprovedSubmitters().get_list().keys()

        if os.path.isfile(paths.TOURNEY_STATE_FILE):
            state_from_file = json.load(open(paths.TOURNEY_STATE_FILE, 'r'))
            self.initialise_state_from_file(approved_submitters, state_from_file)
        else:
            self.initialise_state(approved_submitters)

    def initialise_state(self, approved_submitters):
        for test_submitter in approved_submitters:
            self.state[test_submitter] = {
                'latest_submission_date': None,
                'num_tests': {},
                'test_results': {}
            }

            test_results = {}
            for prog_submitter in approved_submitters:
                if test_submitter != prog_submitter:
                    test_results[prog_submitter] = self.create_default_testset()

            self.state[test_submitter]['test_results'] = test_results

    def initialise_state_from_file(self, approved_submitters, state_from_file):
        # previous result may be able to be copied into new state
        for test_submitter in approved_submitters:
            self.state[test_submitter] = {'latest_submission_date': None,
                                          'num_tests': {},
                                          'test_results': {}}

            for prog_submitter in approved_submitters:
                if test_submitter == prog_submitter:
                    continue
                elif test_submitter in state_from_file.keys() and \
                        prog_submitter in state_from_file[test_submitter]['test_results'].keys():
                    self.get_submitter_results(test_submitter)[prog_submitter] = \
                        state_from_file[test_submitter]['test_results'][prog_submitter]
                    self.state[test_submitter]['latest_submission_date'] = \
                        state_from_file[test_submitter]['latest_submission_date']
                    self.state[test_submitter]['num_tests'] = \
                        state_from_file[test_submitter]['num_tests']
                else:
                    self.get_submitter_results(test_submitter)[prog_submitter] = self.create_default_testset()

    def save_to_file(self):
        json.dump(self.state, open(paths.TOURNEY_STATE_FILE, 'w'), indent=4, sort_keys=True)

    @staticmethod
    def create_default_testset() -> TestSet:
        """
        Create a test set where all values are NOT_TESTED
        testset[test][prog] = TestResult
        :return:
        """
        assg = AssignmentConfig().get_assignment()
        testset = TestSet({})
        for test in assg.get_test_list():
            testset[test] = {}
            for prog in assg.get_programs_list():
                testset[test][prog] = TestResult.NOT_TESTED
        return testset

    def get_valid_submitters(self):
        """
        Provide the list of submitters who have successfully made a valid submission
        :return:
        """
        return [submitter for submitter in self.state.keys() if os.path.isdir(paths.get_tourney_dir(submitter))]

    def get_bugs_detected(self, tester: Submitter, test: Test) -> int:
        bugs_detected = 0
        for testee in self.get_submitters():
            if testee != tester:
                for prog in AssignmentConfig().get_assignment().get_programs_list():
                    if self.get(tester, testee, test, prog) in [TestResult.BUG_FOUND, TestResult.TIMEOUT]:
                        bugs_detected += 1
        return bugs_detected

    def get_tests_evaded(self, testee: Submitter, prog: Prog) -> int:
        tests_evaded = 0

        for tester in self.get_submitters():
            if testee != tester:
                for test in AssignmentConfig().get_assignment().get_test_list():
                    if self.get(tester, testee, test, prog) == TestResult.NO_BUGS_DETECTED:
                        tests_evaded += 1
        return tests_evaded

    def invalidate_prog(self, submitter: Submitter, prog: Prog):
        """
        If a program is found to be invalid, zero its score by marking it as detected by all tests
        :param submitter: the submitter whose program is invalid
        :param prog: the program that is invalid
        """
        for tester in self.get_submitters():
            if submitter != tester:
                for test in AssignmentConfig().get_assignment().get_test_list():
                    self.get_submitter_results(tester)[submitter][test][prog] = TestResult.BUG_FOUND

    def set_time_of_submission(self, submitter: Submitter, time_of_submission: str):
        self.state[submitter]['latest_submission_date'] = time_of_submission

    def set_number_of_tests(self, submitter: Submitter, num_tests: dict):
        self.state[submitter]['num_tests'] = num_tests

    def set(self, tester: Submitter, testee: Submitter, testset: TestSet):
        self.get_submitter_results(tester)[testee] = testset

    def get(self, tester: Submitter, testee: Submitter, test: Test, prog: Prog) -> TestResult:
        return self.get_submitter_results(tester)[testee][test][prog]

    def get_submitters(self) -> [Submitter]:
        return self.state.keys()

    def get_submitter_results(self, submitter: Submitter):
        return self.state[submitter]['test_results']

    def get_num_tests(self, submitter: Submitter):
        return self.state[submitter]['num_tests']

    def get_state(self):
        return self.state
