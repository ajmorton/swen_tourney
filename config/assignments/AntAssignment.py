import math
import os
import re
import subprocess

from config.assignments.AbstractAssignment import AbstractAssignment
from util import paths
from util.funcs import print_tourney_error
from util.types import *


class AntAssignment(AbstractAssignment):

    def __init__(self, source_assg_dir: FilePath):
        super().__init__(source_assg_dir)
        self.tests_list = sorted(os.listdir(self.get_source_assg_dir() + "/tests"))
        self.progs_list = sorted(
            [prog for prog in os.listdir(self.get_source_assg_dir() + "/programs") if prog != 'original'])

    def get_test_list(self) -> [Test]:
        return self.tests_list

    def get_programs_list(self) -> [Prog]:
        return self.progs_list

    def run_test(self, test: Test, prog: Prog, submission_dir: FilePath) -> (TestResult, str):

        result = subprocess.run(
            "ant test -Dtest=\"{}\" -Dprogram=\"{}\"".format(test, prog),
            shell=True, cwd=submission_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        if "Parallel execution timed out" in result.stderr:
            return TestResult.TIMEOUT, result.stdout
        elif result.returncode == 0:
            return TestResult.NO_BUGS_DETECTED, result.stdout
        else:
            return TestResult.BUG_FOUND, result.stdout

    def get_num_tests(self, traces: str) -> int:
        num_tests_regex = re.search("Tests run: ([0-9]+)", traces)
        if num_tests_regex is not None:
            return int(num_tests_regex.group(1))
        else:
            # Assumed default test count of 20
            print_tourney_error("Cannot find regex 'Tests run: ([0-9]+)' in traces:\n" + traces)
            return 20

    def prep_submission(self, submission_dir: FilePath, destination_dir: FilePath):

        # copy across the tests
        subprocess.run("rm -rf {}".format(destination_dir + "/tests"), shell=True)
        subprocess.run("cp -rf {} {}".format(submission_dir + "/tests", destination_dir), shell=True)

        # copy across the programs, excluding 'original'
        for program in self.get_programs_list():
            subprocess.run("rm -rf {}".format(destination_dir + "/programs/" + program), shell=True)
            subprocess.run(
                "cp -rf {} {}".format(submission_dir + "/programs/" + program, destination_dir + "/programs"),
                shell=True
            )

    def detect_new_tests(self, new_submission: FilePath, old_submission: FilePath) -> [Test]:

        if not os.path.isdir(old_submission):
            # if there is no previous submission then all tests are new
            return self.get_test_list()

        new_tests = []
        tests_path = "/tests/"
        for test in self.get_test_list():
            diff = subprocess.run(
                "diff -r {} {}".format(new_submission + tests_path + test, old_submission + tests_path + test),
                stdout=subprocess.PIPE,
                shell=True
            )
            if diff.returncode != 0:
                new_tests.append(test)

        return new_tests

    def detect_new_progs(self, new_submission: FilePath, old_submission: FilePath) -> [Prog]:
        if not os.path.isdir(old_submission):
            # if there is no previous submission then all tests are new
            return self.get_programs_list()

        new_progs = []
        programs_path = "/programs/"
        for prog in self.get_programs_list():
            diff = subprocess.run(
                "diff -r {} {}".format(new_submission + programs_path + prog, old_submission + programs_path + prog),
                stdout=subprocess.PIPE,
                shell=True
            )
            if diff.returncode != 0:
                new_progs.append(prog)

        return new_progs

    def prep_test_stage(self, tester: Submitter, testee: Submitter, test_stage_dir: FilePath):

        test_stage_code_dir = test_stage_dir
        tester_code_dir = paths.get_tourney_dir(tester)
        testee_code_dir = paths.get_tourney_dir(testee)

        # make sure folders that are required are present
        if not os.path.isdir(test_stage_code_dir + "/.depcache"):
            subprocess.run("mkdir {}".format(test_stage_code_dir + "/.depcache"), shell=True)

        if not os.path.isdir(test_stage_code_dir + "/classes"):
            subprocess.run("mkdir {}".format(test_stage_code_dir + "/classes"), shell=True)

        # clean test_stage_dir of previous tests
        tester_files = ["/.depcache/tests", "/tests", "/classes/tests"]
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

    def compute_normalised_prog_score(self, submitter_score: float, best_score: float) -> float:
        if best_score == 0:
            return 0
        else:
            score = (submitter_score / best_score)
            score *= 2.5  # best score possible is 1. Multiply by 2.5 to scale to 2.5
        return round(score, 2)

    def compute_normalised_test_score(self, submitter_score: float, best_score: float, num_tests: int) -> float:
        if best_score == 0:
            return 0
        else:
            score = ((submitter_score / best_score) / (math.log(num_tests) + 10))
            score *= 25  # best score possible is 0.1. Multiply by 25 to scale to 2.5
        return round(score, 2)

    def get_diffs(self, submission_dir: FilePath) -> Dict:

        diffs = {}
        for prog in self.get_programs_list():
            prog_diff = subprocess.run("diff -r {} {}".format("original", prog), cwd=submission_dir + "/programs/",
                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            diffs[prog] = prog_diff.stdout.strip()

        return diffs
