from abc import ABCMeta, abstractmethod
from tournament.util.types.basetypes import TestResult


class AbstractAssignment(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get_source_assg_dir() -> str:
        """
        Return the path to the original source code of the assignment
        :return: the path to the original source code of the assignment
        """

    @staticmethod
    @abstractmethod
    def get_test_list() -> [str]:
        """
        Get the list of tests in the assignment
        :return: The list of tests in the assignment
        """
        raise NotImplementedError("Error: get_tests is not implemented")

    @staticmethod
    @abstractmethod
    def get_programs_list() -> [str]:
        """
        Get the list of programs under test in the assignment
        :return: The list of programs under test in the assignment
        """
        raise NotImplementedError("Error: get_programs_under_test is not implemented")

    @staticmethod
    @abstractmethod
    def run_test(test: str, prog: str, submission_dir: str) -> TestResult:
        """
        Run a test against a program under test
        :param test: the test suite
        :param prog: the program under test
        :param submission_dir: the directory of the submission
        :return: The result of the test run
        """
        raise NotImplementedError("Error: run_test is not implemented")

    @staticmethod
    @abstractmethod
    def prep_submission(submission_dir: str, destination_dir: str):
        """
        Copy the relevant files from the submitters submission into a destination folder. The destination_dir is
        assumed to be a copy of the original source code for the submission.
        :param submission_dir: The directory of the submission
        :param destination_dir: Where to copy the relevant files to.
                                Assumed to be a copy of the original source assignment.
        """
        raise NotImplementedError("Error: prep_submission is not implemented")

    @staticmethod
    @abstractmethod
    def detect_new_tests(new_submission: str, old_submission: str) -> [str]:
        """
        Compare an old submission with a new submission and identify which tests have been updated
        :param old_submission: the directory of the old submission
        :param new_submission: the directory of the new submission
        :return: the list of tests that have been updated
        """

    @staticmethod
    @abstractmethod
    def detect_new_progs(new_submission: str, old_submission: str) -> [str]:
        """
        Compare an old submission with a new submission and identify which programs under test have been updated
        :param old_submission: the directory of the old submission
        :param new_submission: the directory of the new submission
        :return: the list of programs under test that have been updated
        """

    @staticmethod
    @abstractmethod
    def prep_test_stage(tester: str, testee: str, test_stage_dir: str):
        """
        Prepare a test stage with the tests from the tester and the progs under test from the testee.
        :param tester: the name of the submitter whose tests are to be run
        :param testee: the name of the submitter whose programs under test are to be tested
        :param test_stage_dir: the directory of the test staging area
        """