from tournament.assignments.AbstractAssignment import AbstractAssignment
import os
import subprocess
from tournament.util.types.basetypes import TestResult
import tournament.config.paths as paths


path = os.path.dirname(os.path.abspath(__file__))
source_assg = path + "/ant_assignment"


class AntAssignment(AbstractAssignment):

    @staticmethod
    def get_source_assg_dir() -> str:
        return source_assg

    @staticmethod
    def get_test_list() -> [str]:
        return ["boundary", "partitioning"]

    @staticmethod
    def get_programs_under_test_list() -> [str]:
        return ["mutant-1", "mutant-2", "mutant-3", "mutant-4", "mutant-5"]

    @staticmethod
    def run_test(test: str, prog: str, submission_dir: str) -> TestResult:
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

    @staticmethod
    def prep_submission(submission_dir: str, destination_dir: str):

        # copy across the test folder
        subprocess.run("rm -rf {}".format(destination_dir + "/ant_assignment/test"), shell=True)
        subprocess.run(
            "cp -rf {} {}".format(submission_dir + "/ant_assignment/test", destination_dir + "/ant_assignment")
            , shell=True
        )

        for program in AntAssignment.get_programs_under_test_list():
            # copy across the program
            subprocess.run("rm -rf {}".format(destination_dir + "/ant_assignment/programs/" + program), shell=True)
            subprocess.run(
                "cp -rf {} {}".format(
                    submission_dir + "/ant_assignment/programs/" + program,
                    destination_dir + "/ant_assignment/programs")
                , shell=True
            )


    @staticmethod
    def prep_test_stage(tester: str, testee: str, test_stage_dir: str):

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
