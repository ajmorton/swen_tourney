"""
Configuration for assignments using addressSanitizer and Student created fuzzers to create and detect vulnerabilities
in C code.

Expects the core file structure:
fuzz_assignment
├── Makefile
├── bin
├── build.sh
├── fuzzer
├── poc
├── run_fuzzer.sh
├── run_tests.sh
├── src
└── tests

An example can be found at 'fuzz_assignment' in the same repo as this code

"""
import os
import re
import subprocess
from typing import Dict

from tournament.config.assignments import AbstractAssignment
from tournament.util import FilePath, Prog, Result, Submitter, Test, TestResult
from tournament.util import paths


class FuzzAssignment(AbstractAssignment):
    """ Implementation for assignment using addressSanitizer and fuzzers """

    def __init__(self, source_assg_dir: FilePath):
        super().__init__(source_assg_dir)
        self.tests_list = ["fuzzer"]
        self.progs_list = sorted(
            [prog for prog in os.listdir(self.get_source_assg_dir() + "/src") if prog not in ['original', 'include']])

    def get_test_list(self) -> [Test]:
        return self.tests_list

    def get_programs_list(self) -> [Prog]:
        return self.progs_list

    def progs_identical(self, prog1: Prog, prog2: Prog, submission_dir: FilePath) -> bool:
        diff = subprocess.run(f"diff -rw {prog1} {prog2}", cwd=submission_dir + "/src",
                              shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return diff.returncode == 0

    def run_test(self, test: Test, prog: Prog, submission_dir: FilePath, use_poc: bool = False) -> (TestResult, str):

        if use_poc:
            test_command = f"./run_tests.sh {prog} --use-poc"
        else:
            test_command = f"./run_tests.sh {prog}"

        try:
            try:
                result = subprocess.run(test_command, shell=True, cwd=submission_dir, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=30, check=False)
            except subprocess.TimeoutExpired:
                return TestResult.TIMEOUT, "Took longer than 30 seconds to run"
        except MemoryError:
            # If a prog spams traces to stderr/stdout subprocess can run out of memory and throw a memory exception
            # This tends to be co-morbid with timeout errors
            return TestResult.TIMEOUT, "Memory error when extracting traces"

        stdout = result.stdout.decode('ascii', errors='backslashreplace')

        if result.returncode == 0:
            return TestResult.NO_BUGS_DETECTED, stdout
        elif result.returncode in [1, 134]:
            # The exact error codes that AddressSanitizer returns are to be determined.
            # This will be updated as more codes are discovered
            return TestResult.BUG_FOUND, stdout
        else:
            return TestResult.UNEXPECTED_RETURN_CODE, f"Exit code: {result.returncode}\n{stdout}"

    def get_num_tests(self, traces: str) -> int:
        return 0  # num tests is not needed for fuzz_assignment, as it does not impact the scoring functions

    def prep_submission(self, submission_dir: FilePath, destination_dir: FilePath) -> Result:

        # because student keep submitting binaries and using up all the server space
        subprocess.run("make clean", shell=True, cwd=submission_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
        subprocess.run("rm -rf tests/*", shell=True, cwd=submission_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)

        # copy across the fuzzer and PoCs
        for folder in ['/fuzzer', '/poc']:
            subprocess.run(f"rm -rf {destination_dir + folder}", shell=True, check=True)
            res = subprocess.run(f"cp -rf {submission_dir + folder} {destination_dir}",
                                 shell=True, check=False)
            if res.returncode != 0:
                return Result(False, res.stderr[res.stderr.find(self.get_assignment_name()): ])

        # copy across the programs, excluding 'original' and 'include'
        for program in self.get_programs_list():
            subprocess.run(f"rm -rf {destination_dir}/src/{program}", shell=True, check=True)
            res = subprocess.run(f"cp -rf {submission_dir}/src/{program} {destination_dir}/src",
                                 shell=True, check=False)
            if res.returncode != 0:
                return Result(False, res.stderr[res.stderr.find(self.get_assignment_name()): ])

        # ensure the bin/ folder is empty, submitters haven't pushed binaries
        subprocess.run("make clean", shell=True, cwd=destination_dir, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True, check=True)

        return Result(True, "Preparation successful")

    def compile_prog(self, submission_dir: FilePath, prog: Prog) -> Result:
        compil = subprocess.run(f'CFLAGS="-DDEBUG_NO_PRINTF" make VERSIONS={prog}', cwd=submission_dir,
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                                check=False)
        if compil.returncode != 0:
            return Result(False, compil.stdout)
        return Result(True, "")

    def compile_test(self, submission_dir: FilePath, test: Test) -> Result:
        try:
            # run the fuzzer to generate a list of tests in tests/
            result = subprocess.run("./run_fuzzer.sh", shell=True, cwd=submission_dir, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, universal_newlines=True, timeout=300, check=False)
        except subprocess.TimeoutExpired:
            return Result(False, "Generating tests with ./run_fuzzer.sh timed out after 5 minutes")

        if result.returncode != 0:
            return Result(False, result.stdout)
        return Result(True, "")

    def detect_new_tests(self, new_submission: FilePath, old_submission: FilePath) -> [Test]:
        # Fuzzers generate random tests, and so will need to be rerun every submission regardless of whether
        # the source code for the fuzzer has changed
        return self.get_test_list()

    def detect_new_progs(self, new_submission: FilePath, old_submission: FilePath) -> [Prog]:
        if not os.path.isdir(old_submission):
            # if there is no previous submission then all tests are new
            return self.get_programs_list()

        new_progs = []
        for prog in self.get_programs_list():
            diff = subprocess.run(
                f"diff -r {new_submission}/src/{prog} {old_submission}/src/{prog}",
                stdout=subprocess.PIPE, shell=True, check=False)
            if diff.returncode != 0:
                new_progs.append(prog)

        return new_progs

    def prep_test_stage(self, tester: Submitter, testee: Submitter, test_stage_dir: FilePath):

        test_stage_code_dir = test_stage_dir
        tester_code_dir = paths.get_tourney_dir(tester)
        testee_code_dir = paths.get_tourney_dir(testee)

        # symlink in testers tests
        subprocess.run(f"rm -rf {test_stage_code_dir}/tests", shell=True, check=True)
        subprocess.run(f"ln -s {tester_code_dir}/tests {test_stage_code_dir}/tests",
                       shell=True, check=True)

        # symlink in testees programs
        subprocess.run(f"rm -rf {test_stage_code_dir}/bin", shell=True, check=True)
        subprocess.run(f"ln -s {testee_code_dir}/bin {test_stage_code_dir}/bin",
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
            score = submitter_score / best_score
            score *= 2.5  # best score possible is 1. Multiply by 2.5 to scale to 2.5
        return round(score, 2)

    def get_diffs(self, submission_dir: FilePath) -> Dict:

        diffs = {}
        for prog in self.get_programs_list():
            prog_diff = subprocess.run(f"diff -rw original {prog}", cwd=submission_dir + "/src/",
                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True, check=False)
            diffs[prog] = prog_diff.stdout.strip()

        return diffs

    def check_diff(self, submission_dir: FilePath, prog: Prog) -> Result:

        prog_diff = subprocess.run(f"diff -rw original {prog}", cwd=submission_dir + "/src/",
                                   shell=True, stdout=subprocess.PIPE, text=True, check=False).stdout

        # don't allow dependency changes
        if re.search(r"(<|>)\s*#include", prog_diff):
            return Result(False, f"#includes have been modified:\n\n{prog_diff}")

        # don't allow more than 3 changes (e.g lines added: '66a65,69', deleted: 70d71, or changed: 407c408)
        changes = re.findall(r"\n(.*[0-9]{1,4}(a|c|d)[0-9]{1,4}.*)\n", prog_diff)
        if len(changes) > 3:
            return Result(False, f"Code changed in more than 3 locations: {[chg[0] for chg in changes]}\n\n{prog_diff}")

        # don't allow more than 30 new/modified lines (ignore single line comments //)
        new_lines = [line for line in prog_diff.split('\n') if re.search(r"^>(?!\s*\/\/).*$", line)]
        if len(new_lines) > 30:
            return Result(False, f"More than 30 lines modified (excluding single line // comments):\n\n{prog_diff}")

        return Result(True, "Diff valid")
