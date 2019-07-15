from tournament.assignments.AbstractAssignment import AbstractAssignment
import os
import subprocess
from tournament.util.types.basetypes import TestResult
import tournament.config.paths as paths

class AntAssignment(AbstractAssignment):

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.source_assg = self.path + "/ant_assignment"
        pass

    def get_source_assg_dir(self) -> str:
        return self.source_assg

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

    def prep_test_stage(self, tester: str, testee: str, test_stage_dir: str):

        test_stage_code_dir = test_stage_dir + "/ant_assignment"
        tester_code_dir = paths.TOURNEY_DIR + "/" + tester + "/ant_assignment"
        testee_code_dir = paths.TOURNEY_DIR + "/" + testee + "/ant_assignment"

        # make sure folders that are required are present
        if not os.path.isdir(test_stage_code_dir + "/.depcache"):
            subprocess.run("mkdir {}".format(test_stage_code_dir + "/.depcache"), shell=True)

        if not os.path.isdir(test_stage_code_dir + "/classes"):
            subprocess.run("mkdir {}".format(test_stage_code_dir + "/classes"), shell=True)

        # clean test_stage_dir of previous tests
        tester_files = ["/.depcache/test", "/test", "/classes/test"]
        testee_files = ["/.depcache/programs", "/programs", "/classes/programs"]

        # remove previous files
        for file in tester_files + testee_files:
            subprocess.run("rm -rf {}".format(test_stage_code_dir + file), shell=True)

        # link in files from tester
        for file in tester_files:
            subprocess.run("ln -s {} {}".format(tester_code_dir + file, test_stage_code_dir + file), shell=True)

        # link in files from testee
        for file in testee_files:
            subprocess.run("ln -s {} {}".format(testee_code_dir + file, test_stage_code_dir + file), shell=True)
