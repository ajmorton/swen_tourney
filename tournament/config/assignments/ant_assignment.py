"""
Configuration for assignments using ant and JUnit for testing.

Expects the core file structure:
assignment_name/
├── build.xml
├── programs
│   ├── mutant-1
│   ├── mutant-2
│   ├── ...
│   └── original
└── tests
    ├── Partitioning
    ├── Boundary
    └── ...

An example can be found at 'ant_assignment' in the same repo as this code

"""
import math
import os
import re
import subprocess
from typing import Dict

from tournament.config.assignments import AbstractAssignment
from tournament.util import FilePath, Prog, Result, Submitter, Test, TestResult
from tournament.util import paths, print_tourney_error


class AntAssignment(AbstractAssignment):
    """ Implementation for assignment using ant and Junit """

    def __init__(self, source_assg_dir: FilePath):
        super().__init__(source_assg_dir)
        self.tests_list = sorted(os.listdir(self.get_source_assg_dir() + "/tests"))
        self.progs_list = sorted(
            [prog for prog in os.listdir(self.get_source_assg_dir() + "/programs") if prog != 'original'])

    def get_test_list(self) -> [Test]:
        return self.tests_list

    def get_programs_list(self) -> [Prog]:
        return self.progs_list

    def progs_identical(self, prog1: Prog, prog2: Prog, submission_dir: FilePath) -> bool:
        diff = subprocess.run(f"diff -rw {prog1} {prog2}", cwd=submission_dir + "/programs",
                              shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return diff.returncode == 0

    def run_test(self, test: Test, prog: Prog, submission_dir: FilePath, use_poc: bool = False) -> (TestResult, str):

        result = subprocess.run(
            f"ant test -Dtest=\"{test}\" -Dprogram=\"{prog}\"",
            shell=True, cwd=submission_dir,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=False
        )

        if "Parallel execution timed out" in result.stdout:
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
            print_tourney_error(f"Cannot find regex 'Tests run: ([0-9]+)' in traces:\n{traces}")
            return 20

    def prep_submission(self, submission_dir: FilePath, destination_dir: FilePath) -> Result:

        # copy across the tests
        subprocess.run(f"rm -rf {destination_dir}/tests", shell=True, check=True)
        res = subprocess.run(f"cp -rf {submission_dir}/tests {destination_dir}",
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, text=True)
        if res.returncode != 0:
            return Result(False, res.stderr[res.stderr.find(self.get_assignment_name()): ])

        # copy across the programs, excluding 'original'
        for program in self.get_programs_list():
            subprocess.run(f"rm -rf {destination_dir}/programs/{program}", shell=True, check=True)
            res = subprocess.run(
                f"cp -rf {submission_dir}/programs/{program} {destination_dir}/programs",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, text=True)
            if res.returncode != 0:
                return Result(False, res.stderr[res.stderr.find(self.get_assignment_name()): ])

        return Result(True, "Preparation successful")

    def compile_prog(self, submission_dir: FilePath, prog: Prog) -> Result:
        # program compilation is handled by the ant build script
        return Result(True, "")

    def compile_test(self, submission_dir: FilePath, test: Test) -> Result:
        # program compilation is handled by the ant build script
        return Result(True, "")

    def detect_new_tests(self, new_submission: FilePath, old_submission: FilePath) -> [Test]:

        if not os.path.isdir(old_submission):
            # if there is no previous submission then all tests are new
            return self.get_test_list()

        new_tests = []
        tests_path = "/tests/"
        for test in self.get_test_list():
            diff = subprocess.run(
                f"diff -r {new_submission + tests_path + test} {old_submission + tests_path + test}",
                stdout=subprocess.PIPE, shell=True, check=False)
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
                f"diff -r {new_submission + programs_path + prog} {old_submission + programs_path + prog}",
                stdout=subprocess.PIPE, shell=True, check=False)
            if diff.returncode != 0:
                new_progs.append(prog)

        return new_progs

    def prep_test_stage(self, tester: Submitter, testee: Submitter, test_stage_dir: FilePath):

        test_stage_code_dir = test_stage_dir
        tester_code_dir = paths.get_tourney_dir(tester)
        testee_code_dir = paths.get_tourney_dir(testee)

        # make sure folders that are required are present
        if not os.path.isdir(test_stage_code_dir + "/.depcache"):
            subprocess.run(f"mkdir {test_stage_code_dir}/.depcache", shell=True, check=True)

        if not os.path.isdir(test_stage_code_dir + "/classes"):
            subprocess.run(f"mkdir {test_stage_code_dir}/classes", shell=True, check=True)

        # clean test_stage_dir of previous tests
        tester_files = ["/.depcache/tests", "/tests", "/classes/tests"]
        testee_files = ["/.depcache/programs", "/programs", "/classes/programs"]

        # remove previous files
        for file in tester_files + testee_files:
            subprocess.run(f"rm -rf {test_stage_code_dir + file}", shell=True, check=True)

        # link in files from tester
        for file in tester_files:
            subprocess.run(f"ln -s {tester_code_dir + file} {test_stage_code_dir + file}",
                           shell=True, check=True)

        # link in files from testee
        for file in testee_files:
            subprocess.run(f"ln -s {testee_code_dir + file} {test_stage_code_dir + file}",
                           shell=True, check=True)

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
            prog_diff = subprocess.run(f"diff -rw original {prog}", cwd=submission_dir + "/programs/",
                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True, check=False)
            diffs[prog] = prog_diff.stdout.strip()

        return diffs

    def check_diff(self, submission_dir: FilePath, prog: Prog) -> Result:

        prog_diff = subprocess.run(f"diff -rw original {prog}", cwd=submission_dir + "/programs/",
                                   shell=True, stdout=subprocess.PIPE, text=True, check=False).stdout

        # don't allow dependency changes
        if re.search(r"(<|>)\s*import", prog_diff):
            return Result(False, f"imports have been modified:\n\n{prog_diff}")

        # only allow a single code change (e.g lines added: '66a65,69', deleted: 70d71, or changed: 407c408)
        changes = re.findall(r"\n(.*[0-9]{1,4}(a|c|d)[0-9]{1,4}.*)\n", prog_diff)
        if len(changes) > 1:
            return Result(False, f"Code changed in more than 1 location: {[chg[0] for chg in changes]}\n\n{prog_diff}")

        # don't allow more than 1 new/modified lines (ignore single line comments //)
        new_lines = [line for line in prog_diff.split('\n') if re.search(r"^>(?!\s*\/\/).*$", line)]
        if len(new_lines) > 1:
            return Result(False, f"More than 1 line modified (excluding single line // comments):\n\n{prog_diff}")

        return Result(True, "Diff valid")
