"""
The tournament can be configured for multiple different assignment types.
AbstractAssignment provides an interface that new assignment configurations must implement in order to be
used in the tournament. New assignment configurations should inherit from this class
"""
import os
from abc import ABCMeta, abstractmethod
from typing import Dict

from util.types import FilePath, Prog, Result, Submitter, Test, TestResult


class AbstractAssignment(metaclass=ABCMeta):
    """ Interface for new assignment configurations """

    def __init__(self, source_assg_dir: FilePath):
        self.source_assg = source_assg_dir

    def get_source_assg_dir(self) -> FilePath:
        """
        Return the path to the original source code of the assignment
        :return: the path to the original source code of the assignment
        """
        return self.source_assg

    def get_assignment_name(self) -> str:
        """
        Get the name of the source assignment.
        :return: the name of the source assignment
        """
        return os.path.basename(self.source_assg.rstrip("/"))

    @abstractmethod
    def get_test_list(self) -> [Test]:
        """
        Get the list of tests in the assignment
        :return: The list of tests in the assignment
        """
        raise NotImplementedError("Error: get_tests is not implemented")

    @abstractmethod
    def get_programs_list(self) -> [Prog]:
        """
        Get the list of programs under test in the assignment
        :return: The list of programs under test in the assignment
        """
        raise NotImplementedError("Error: get_programs_under_test is not implemented")

    @abstractmethod
    def is_prog_unique(self, prog: Prog, submission_dir: FilePath) -> Result:
        """
        Determine whether the specified program under test is unique among all the programs in a submission
        :param prog: the program to check
        :param submission_dir: the submission to check
        :return: Whether the program is unique
        """

    @abstractmethod
    def run_test(self, test: Test, prog: Prog, submission_dir: FilePath, use_poc: bool = False,
                 compile_prog: bool = False) -> (TestResult, str):
        """
        Run a test against a program under test.
        :param test: the test suite
        :param prog: the program under test
        :param submission_dir: the directory of the submission
        :param use_poc: some assignments will use tests with an element of randomness to them - e.g. fuzzers -
        when validating that a program has a valid bug a proof of concept (poc) may be used instead
        :param compile_prog: whether the program requires compilation before running the test
        :return: The result of the test run
        """
        raise NotImplementedError("Error: run_test is not implemented")

    @abstractmethod
    def get_num_tests(self, traces: str) -> int:
        """
        Determine the number of tests in a testsuite from its traces
        :param traces: the traces from running a test suite
        :return: the number of tests run by the test suite
        """

    @abstractmethod
    def prep_submission(self, submission_dir: FilePath, destination_dir: FilePath) -> Result:
        """
        Copy the relevant files from the submitters submission into a destination folder. The destination_dir is
        assumed to be a copy of the original source code for the submission.
        :param submission_dir: The directory of the submission
        :param destination_dir: Where to copy the relevant files to.
                                Assumed to be a copy of the original source assignment.
        :return: whether the submission was prepared successfully
        """
        raise NotImplementedError("Error: prep_submission is not implemented")

    @abstractmethod
    def detect_new_tests(self, new_submission: FilePath, old_submission: FilePath) -> [Test]:
        """
        Compare an old submission with a new submission and identify which tests have been updated
        :param old_submission: the directory of the old submission
        :param new_submission: the directory of the new submission
        :return: the list of tests that have been updated
        """
        raise NotImplementedError("Error: detect_new_tests is not implemented")

    @abstractmethod
    def detect_new_progs(self, new_submission: FilePath, old_submission: FilePath) -> [Prog]:
        """
        Compare an old submission with a new submission and identify which programs under test have been updated
        :param old_submission: the directory of the old submission
        :param new_submission: the directory of the new submission
        :return: the list of programs under test that have been updated
        """
        raise NotImplementedError("Error: detect_new_progs is not implemented")

    @abstractmethod
    def prep_test_stage(self, tester: Submitter, testee: Submitter, test_stage_dir: FilePath):
        """
        Prepare a test stage with the tests from the tester and the progs under test from the testee.
        :param tester: the name of the submitter whose tests are to be run
        :param testee: the name of the submitter whose programs under test are to be tested
        :param test_stage_dir: the directory of the test staging area
        """
        raise NotImplementedError("Error: prep_test_stage is not implemented")

    @abstractmethod
    def compute_normalised_test_score(self, submitter_score: float, best_score: float, num_tests: int) -> float:
        """
        Compute a submitters test score normalised against the best test score in the tournament.
        :return: the submitters normalised test score
        """
        raise NotImplementedError("Error: compute_normalised_test_score is not implemented")

    @abstractmethod
    def compute_normalised_prog_score(self, submitter_score: float, best_score: float) -> float:
        """
        Compute a submitters prog score normalised against the best prog score in the tournament.
        :return: the submitters normalised prog score
        """
        raise NotImplementedError("Error: compute_normalised_test_score is not implemented")

    @abstractmethod
    def get_diffs(self, submission_dir: FilePath) -> Dict:
        """
        Return the diffs between the original source code and a submitters provided programs
        :param submission_dir: the submission to fetch the diffs for
        :return: the diffs between the original source code and a submitters provided programs
        """
