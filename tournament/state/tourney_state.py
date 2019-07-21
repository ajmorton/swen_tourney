import os
import json

import tournament.config.config as config
import tournament.config.paths as paths
import tournament.util.funcs as funcs
from tournament.util.types.basetypes import *


class TourneyState:
    """
    Maintain a record of which students tests have detected or missed which student's bugged progs.
    This can be saved and loaded from a json file to help mitigate crashes.
    """

    def __init__(self):
        self.state = {}

        # TODO check for missing approved_submitters file
        approved_submitters = json.load(open(paths.SUBMITTERS_LIST, 'r'))

        if os.path.isfile(paths.TOURNEY_STATE_FILE):
            state_from_file = json.load(open(paths.TOURNEY_STATE_FILE, 'r'))
            self.initialise_state_from_file(approved_submitters, state_from_file)
        else:
            self.initialise_state(approved_submitters)

    def initialise_state(self, approved_submitters):
        for test_submitter in approved_submitters.keys():
            self.state[test_submitter] = {
                'email': approved_submitters[test_submitter]['email'],
                'latest_submission_date': None,
                'test_results': {}
            }

            test_results = {}
            for prog_submitter in approved_submitters.keys():
                if test_submitter != prog_submitter:
                    test_results[prog_submitter] = self.create_default_testset()

            self.state[test_submitter]['test_results'] = test_results

    def initialise_state_from_file(self, approved_submitters, state_from_file):
        # previous result may be able to be copied into new state
        for test_submitter in approved_submitters.keys():
            self.state[test_submitter] = {'email': approved_submitters[test_submitter]['email'],
                                          'latest_submission_date': None,
                                          'test_results': {}
                                          }

            for prog_submitter in approved_submitters.keys():
                if test_submitter == prog_submitter:
                    continue
                if test_submitter in state_from_file.keys() and \
                        prog_submitter in state_from_file[test_submitter]['test_results'].keys():
                    self.get_submitter_results(test_submitter)[prog_submitter] = \
                        state_from_file[test_submitter]['test_results'][prog_submitter]
                    self.state[test_submitter]['latest_submission_date'] = \
                        state_from_file[test_submitter]['latest_submission_date']
                else:
                    self.get_submitter_results(test_submitter)[prog_submitter] = self.create_default_testset()

    def save_to_file(self):
        json.dump(self.state, open(paths.TOURNEY_STATE_FILE, 'w'), indent=4)

    @staticmethod
    def create_default_testset() -> TestSet:
        """
        Create a test set where all values are NOT_TESTED
        testset[test][prog] = TestResult
        :return:
        """
        testset = TestSet({})
        for test in config.assignment.get_test_list():
            testset[test] = {}
            for prog in config.assignment.get_programs_list():
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
                for prog in config.assignment.get_programs_list():
                    if self.get(tester, testee, test, prog) in [TestResult.BUG_FOUND, TestResult.TIMEOUT]:
                        bugs_detected += 1
        return bugs_detected

    def get_tests_evaded(self, testee: Submitter, prog: Prog) -> int:
        tests_evaded = 0

        for tester in self.get_submitters():
            if testee != tester:
                for test in config.assignment.get_test_list():
                    if self.get(tester, testee, test, prog) == TestResult.NO_BUGS_DETECTED:
                        tests_evaded += 1
        return tests_evaded

    def print(self):
        funcs.print_dict_sorted(self.state)

    def set_time_of_submission(self, submitter: Submitter, time_of_submission: str):
        self.state[submitter]['latest_submission_date'] = time_of_submission

    def set(self, tester: Submitter, testee: Submitter, testset: TestSet):
        self.get_submitter_results(tester)[testee] = testset

    def get(self, tester: Submitter, testee: Submitter, test: Test, prog: Prog) -> TestResult:
        return self.get_submitter_results(tester)[testee][test][prog]

    def get_submitters(self) -> [Submitter]:
        return self.state.keys()

    def get_submitter_results(self, submitter: Submitter):
        return self.state[submitter]['test_results']

    def get_state(self):
        return self.state
