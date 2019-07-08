from tournament.configs.AbstractConfig import AbstractConfig
import os
import subprocess
from typing import Tuple
from tournament.util.types import TestResult


class AntConfig(AbstractConfig):

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.source_assg = self.path + "/source_assg"
        pass

    def get_test_list(self) -> [str]:
        return ["boundary", "partitioning"]

    def get_programs_under_test_list(self) -> [str]:
        return ["mutant-1", "mutant-2", "mutant-3", "mutant-4", "mutant-5"]

    def validate_tests(self, submission_dir: str) -> Tuple[bool, str]:
        """
        Run the boundary and partitioning tests against the original non-bugged source code.
        Return true if both tests detect no errors. Return false if either test falsely returns an error.
        :param submission_dir: The directory of the submission
        :return: (tests_valid, validation_traces)
        """

        results = self.run_tests(['original'], ['boundary', 'partitioning'], submission_dir)

        validation_traces = "Validation results:"
        tests_valid = True

        for [mutant, test, test_passed, test_timeout] in results:
            if test_timeout:
                validation_traces += "\n{} {} test FAIL - Timeout".format(mutant, test)
            elif not test_passed:
                validation_traces += "\n{} {} test FAIL - Test falsely reports an error in original code".format(mutant, test)
            else:
                validation_traces += "\n{} {} test SUCCESS - no bugs detected".format(mutant, test)

            tests_valid = tests_valid and test_passed and not test_timeout

        return tests_valid, validation_traces

    def validate_mutants(self, submission_dir: str) -> Tuple[bool, str]:
        """
        Run the submission's (already validated) tests against the submissions mutants.
        All of the mutants must be caught by the tests. Return false if any mutant does not
        get caught by the submitters provided tests
        :param submission_dir: The directory of the submission
        :return: (mutants_valid, validation_traces)
        """

        results = self.run_tests(
            ['mutant-1', 'mutant-2', 'mutant-3', 'mutant-4', 'mutant-5'], ['boundary', 'partitioning'], submission_dir
        )

        validation_traces = "Validation results:"
        mutants_valid = True

        for [mutant, test, test_passed, test_timeout] in results:
            if test_timeout:
                validation_traces += "\n{} {} test FAIL - Timeout".format(mutant, test)
            elif test_passed:
                validation_traces += "\n{} {} test FAIL - mutant not detected by test".format(mutant, test)
            else:
                validation_traces += "\n{} {} test SUCCESS - no bugs detected".format(mutant, test)

            mutants_valid = mutants_valid and not test_passed and not test_timeout

        return mutants_valid, validation_traces

    def run_test(self, test: str, mutant: str, submission_dir: str) -> TestResult:
        result = subprocess.run(
            ['ant {} -Dprogram="{}"'.format(test, mutant)], shell=True, cwd=submission_dir + "/ant_assignment",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        if "Parallel execution timed out" in result.stderr:
            return TestResult.TIMEOUT
        elif result.returncode == 0:
            return TestResult.TEST_PASSED
        else:
            return TestResult.TEST_FAILED

    def run_tests(self, mutants: [str], tests: [str], submission_dir: str) -> [str, str, bool, bool]:
        """
        :param mutants: List of mutants to test
        :param tests: List of tests to perform on the mutants
        :param submission_dir: the directory of the submission
        :return: a table of [mutant, test, test_passed, test_timeout]
        """

        results = []

        for mutant in mutants:
            for test in tests:

                result = subprocess.run(
                    ['ant {} -Dprogram="{}"'.format(test, mutant)], shell=True, cwd=submission_dir + "/ant_assignment",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                )

                test_passed = result.returncode == 0
                test_timeout = "Parallel execution timed out" in result.stderr

                results.append([mutant, test, test_passed, test_timeout])

        return results

    def prep_submission(self, submission_dir: str) -> None:
        """
        Make sure that the build.xml and programs/original directory are up to date with the original source assignment
        :param submission_dir: The directory of the submission
        """

        test_dir = submission_dir + "/ant_assignment"

        # replace build.xml with the one from the source assignment
        source_assg_build = self.source_assg + "/build.xml"
        submission_build = "build.xml"
        subprocess.run('cp {} {}'.format(source_assg_build, submission_build), shell=True, cwd=test_dir)

        # diff the submissions programs/original dir with the source assignments.
        # If they differ replace it with the source assignments
        source_assg_original_dir = self.source_assg + "/programs/original"
        submission_original_dir = "programs/original"
        diff = subprocess.run(
            'diff -r {} {}'.format(source_assg_original_dir, submission_original_dir), shell=True, cwd=test_dir
        )

        if diff.returncode != 0:
            subprocess.run('rm -r {}'.format(submission_original_dir), shell=True, cwd=test_dir)
            subprocess.run('ln -s {} {}'.format(
                source_assg_original_dir, submission_original_dir), shell=True, cwd=test_dir
            )
