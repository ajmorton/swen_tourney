from config.assignments.AbstractAssignment import AbstractAssignment
from util.types import *


class DefaultAssignment(AbstractAssignment):

    @staticmethod
    def get_source_assg_dir() -> FilePath:
        pass

    @staticmethod
    def get_test_list() -> [Test]:
        pass

    @staticmethod
    def get_programs_list() -> [Prog]:
        pass

    @staticmethod
    def run_test(test: Test, prog: Prog, submission_dir: FilePath) -> TestResult:
        pass

    @staticmethod
    def prep_submission(submission_dir: FilePath, destination_dir: FilePath):
        pass

    @staticmethod
    def detect_new_tests(new_submission: FilePath, old_submission: FilePath) -> [Test]:
        pass

    @staticmethod
    def detect_new_progs(new_submission: FilePath, old_submission: FilePath) -> [Prog]:
        pass

    @staticmethod
    def prep_test_stage(tester: Submitter, testee: Submitter, test_stage_dir: FilePath):
        pass

    @staticmethod
    def compute_normalised_test_score(submitter_score: float, best_score: float) -> float:
        pass

    @staticmethod
    def compute_normalised_prog_score(submitter_score: float, best_score: float) -> float:
        pass
