from tournament.assignments.AbstractAssignment import AbstractAssignment
import os
import subprocess
from tournament.util.types.basetypes import TestResult


class AntAssignment(AbstractAssignment):

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.source_assg = self.path + "/source_assg"
        pass

    def get_test_list(self) -> [str]:
        return ["boundary", "partitioning"]

    def get_programs_under_test_list(self) -> [str]:
        return ["mutant-1", "mutant-2", "mutant-3", "mutant-4", "mutant-5"]

    def run_test(self, test: str, prog: str, submission_dir: str) -> TestResult:
        result = subprocess.run(
            ['ant {} -Dprogram="{}"'.format(test, prog)], shell=True, cwd=submission_dir + "/ant_assignment",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        if "Parallel execution timed out" in result.stderr:
            return TestResult.TIMEOUT
        elif result.returncode == 0:
            return TestResult.TEST_PASSED
        else:
            return TestResult.TEST_FAILED

    def prep_submission(self, submission_dir: str):
        test_dir = submission_dir + "/ant_assignment"

        # replace build.xml with the one from the source assignment
        subprocess.run('ln -sf {} {}'.format(self.source_assg + "/build.xml", "build.xml"), shell=True, cwd=test_dir)

        # replace programs/original dir with the source assignment's.
        subprocess.run('rm -r {}'.format("programs/original"), shell=True, cwd=test_dir)
        subprocess.run(
            'ln -s {} {}'.format(self.source_assg + "/programs/original", "programs/original"), shell=True, cwd=test_dir
        )

