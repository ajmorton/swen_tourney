from abc import ABCMeta, abstractmethod
from tournament.util.types.basetypes import TestResult


class AbstractAssignment(metaclass=ABCMeta):

    @abstractmethod
    def get_source_assg_dir(self) -> str:
        """
        Return the path to the original source code of the assignment
        :return: the path to the original source code of the assignment
        """

    @abstractmethod
    def get_test_list(self) -> [str]:
        """
        Get the list of tests in the assignment
        :return: The list of tests in the assignment
        """
        raise NotImplementedError("Error: get_tests is not implemented")

    @abstractmethod
    def get_programs_under_test_list(self) -> [str]:
        """
        Get the list of programs under test in the assignment
        :return: The list of programs under test in the assignment
        """
        raise NotImplementedError("Error: get_programs_under_test is not implemented")

    @abstractmethod
    def run_test(self, test: str, prog: str, submission_dir: str) -> TestResult:
        """
        Run a test against a program under test
        :param test: the test suite
        :param prog: the program under test
        :param submission_dir: the directory of the submission
        :return: The result of the test run
        """
        raise NotImplementedError("Error: run_test is not implemented")

    @abstractmethod
    def prep_submission(self, submission_dir: str):
        """
        Ensure that files in a submission that should not be changed by the submitter are unchanged
        :param submission_dir: The directory of the submission
        """
        raise NotImplementedError("Error: prep_submission is not implemented")

    @abstractmethod
    def prep_test_stage(self, tester: str, testee: str, test_stage_dir: str):
        """
        Prepare a test stage with the tests from the tester and the progs under test from the testee.
        :param tester: the name of the submitter whose tests are to be run
        :param testee: the name of the submitter whose programs under test are to be tested
        :param test_stage_dir: the directory of the test staging area
        """