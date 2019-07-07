
from abc import ABCMeta, abstractmethod


class AbstractConfig(metaclass=ABCMeta):

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

