
from abc import ABCMeta, abstractmethod


class AbstractConfig(metaclass=ABCMeta):

    @abstractmethod
    def get_test_list(self) -> [str]:
        """
        Get the list of tests in the assignmenr
        :return: The list of tests in the assignment [str]
        """
        raise NotImplementedError("Error: get_tests is not implemented")

    @abstractmethod
    def get_programs_under_test_list(self) -> [str]:
        """
        Get the list of programs under test in the assignmenr
        :return: The list of programs under test in the assignment [str]
        """
        raise NotImplementedError("Error: get_programs_under_test is not implemented")

    @abstractmethod
    def validate_tests(self, submission_dir: str) -> bool:
        """
        validate that all tests are valid for running in a tournament
        :param submission_dir: the path to the submission to validate
        :return: True if all tests are valid
        """
        raise NotImplementedError("Error: validate_tests is not implemented")

    @abstractmethod
    def validate_mutants(self, submission_dir:str) -> bool:
        """
        validate that all mutants are valid for running in a tournament
        :param submission_dir: the path to the submission to validate
        :return: True if all mutants are valid
        """
        raise NotImplementedError("Error: validate_mutants is not implemented")

