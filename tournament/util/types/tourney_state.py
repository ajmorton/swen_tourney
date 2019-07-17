import os
import json

import tournament.config.config as config
from tournament.util.types.basetypes import TestResult, TestSet
import tournament.config.paths as paths
import tournament.util.funcs as funcs


class TourneyState:
    """
    Maintain a record of which students tests have detected or missed which student's bugged progs.
    This can be saved and loaded from a json file to help mitigate crashes.
    """

    def __init__(self):
        self.state = {}

        # TODO check for missing approved_submitters.txt
        with open(paths.SUBMITTERS_LIST, 'r') as submitters_file:
            submitters_list = [line.strip() for line in submitters_file]

        if os.path.isfile(paths.TOURNEY_STATE_FILE):
            # TODO error handling for this file
            with open(paths.TOURNEY_STATE_FILE, 'r') as infile:
                state_from_file = json.load(infile)
                self.initialise_state_from_file(submitters_list, state_from_file)
        else:
            self.initialise_state(submitters_list)

    def initialise_state(self, submitters_list):
        for test_submitter in submitters_list:
            self.state[test_submitter] = {}
            for prog_submitter in submitters_list:
                if test_submitter == prog_submitter:
                    continue

                self.state[test_submitter][prog_submitter] = self.create_default_testset()

    def initialise_state_from_file(self, submitters_list, state_from_file):
        # previous result may be able to be copied into new state
        for test_submitter in submitters_list:
            self.state[test_submitter] = {}
            for prog_submitter in submitters_list:
                if test_submitter == prog_submitter:
                    continue
                if test_submitter in state_from_file.keys() and \
                        prog_submitter in state_from_file[test_submitter].keys():
                    self.state[test_submitter][prog_submitter] = state_from_file[test_submitter][prog_submitter]
                else:
                    self.state[test_submitter][prog_submitter] = self.create_default_testset()

    def save_to_file(self):
        with open(paths.TOURNEY_STATE_FILE, 'w') as outfile:
            json.dump(self.state, outfile)

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
        return [submitter for submitter in self.state.keys() if os.path.isdir(paths.TOURNEY_DIR + "/" + submitter)]

    def print(self):
        funcs.print_dict_sorted(self.state)

    def set(self, tester: str, testee: str, testset):
        self.state[tester][testee] = testset

    def get(self, tester: str, testee: str, test: str, prog: str):
        return self.state[tester][testee][test][prog]
