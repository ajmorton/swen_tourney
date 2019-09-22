import os
import subprocess
from typing import Dict

from config.assignments.abstract_assignment import AbstractAssignment
from util import paths
from util.types import FilePath, Prog, Result, Submitter, Test, TestResult


class FuzzAssignment(AbstractAssignment):

    def __init__(self, source_assg_dir: FilePath):
        super().__init__(source_assg_dir)
        self.tests_list = ["fuzzer"]
        self.progs_list = sorted(
            [prog for prog in os.listdir(self.get_source_assg_dir() + "/src") if prog not in ['original', 'include']])

    def get_test_list(self) -> [Test]:
        return self.tests_list

    def get_programs_list(self) -> [Prog]:
        return self.progs_list

    def is_prog_unique(self, prog: Prog, submission_dir: FilePath) -> Result:
        other_progs = [p for p in self.get_programs_list() if p != prog]
        for other_prog in other_progs:
            diff = subprocess.run("diff -rw {} {}".format(prog, other_prog), cwd=submission_dir + "/src",
                                  shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if diff.returncode == 0:
                return Result((False, "Duplicate of {}".format(other_prog)))
        return Result((True, "No duplicates found"))

    def run_test(self, test: Test, prog: Prog, submission_dir: FilePath, use_poc: bool = False,
                 compile_prog: bool = False) -> (TestResult, str):

        if compile_prog:
            compil = subprocess.run('CFLAGS="-DDEBUG_NO_PRINTF" make VERSIONS={}'.format(prog), shell=True,
                                    cwd=submission_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    universal_newlines=True)
            if compil.returncode != 0:
                return TestResult.COMPILATION_FAILED, compil.stdout

        if use_poc:
            test_command = "./run_tests.sh {} --use-poc".format(prog)
        else:
            test_command = "./run_tests.sh {}".format(prog)

        try:
            try:
                # Note: Timeout does not work correctly when shell=True, stdout/stderr are written to pipes, and the
                # subprocess spawns children. The original process is killed, but the children aren't and will hold onto
                # the pipes until they terminate. The end result will still be a timeout, but it will take longer than
                # 30 seconds to terminate
                result = subprocess.run(test_command, shell=True, cwd=submission_dir, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=30)
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
            return TestResult.UNEXPECTED_RETURN_CODE, "Exit code: {}\n".format(result.returncode) + stdout

    def get_num_tests(self, traces: str) -> int:
        return 0  # num tests is not needed for fuzz_assignment, as it does not impact the scoring functions

    def prep_submission(self, submission_dir: FilePath, destination_dir: FilePath) -> Result:

        # because student keep submitting binaries and using up all the server space
        subprocess.run("make clean", shell=True, cwd=submission_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run("rm -rf tests/*", shell=True, cwd=submission_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # copy across the fuzzer and PoCs
        for folder in ['/fuzzer', '/poc']:
            subprocess.run("rm -rf {}".format(destination_dir + folder), shell=True)
            subprocess.run("cp -rf {} {}".format(submission_dir + folder, destination_dir), shell=True)

        # copy across the programs, excluding 'original' and 'include'
        for program in self.get_programs_list():
            subprocess.run("rm -rf {}".format(destination_dir + "/src/" + program), shell=True)
            subprocess.run("cp -rf {} {}".format(submission_dir + "/src/" + program, destination_dir + "/src"),
                           shell=True)

        # ensure the bin/ folder is empty, submitters haven't pushed binaries
        subprocess.run("make clean", shell=True, cwd=destination_dir, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True)

        try:
            # run the fuzzer to generate a list of tests in tests/
            subprocess.run("./run_fuzzer.sh", shell=True, cwd=destination_dir, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, universal_newlines=True, timeout=300)
        except subprocess.TimeoutExpired:
            return Result((False, "Generating tests with ./run_fuzzer.sh timed out after 10 minutes"))

        return Result((True, "Preparation successful"))

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
                "diff -r {} {}".format(new_submission + "/src/" + prog, old_submission + "/src/" + prog),
                stdout=subprocess.PIPE, shell=True)
            if diff.returncode != 0:
                new_progs.append(prog)

        return new_progs

    def prep_test_stage(self, tester: Submitter, testee: Submitter, test_stage_dir: FilePath):

        test_stage_code_dir = test_stage_dir
        tester_code_dir = paths.get_tourney_dir(tester)
        testee_code_dir = paths.get_tourney_dir(testee)

        # symlink in testers tests
        subprocess.run("rm -rf {}".format(test_stage_code_dir + "/tests"), shell=True)
        subprocess.run("ln -s {} {}".format(tester_code_dir + "/tests", test_stage_code_dir + "/tests"), shell=True)

        # symlink in testees programs
        subprocess.run("rm -rf {}".format(test_stage_code_dir + "/bin"), shell=True)
        subprocess.run("ln -s {} {}".format(testee_code_dir + "/bin", test_stage_code_dir + "/bin"), shell=True)

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
            prog_diff = subprocess.run("diff -rw {} {}".format("original", prog), cwd=submission_dir + "/src/",
                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            diffs[prog] = prog_diff.stdout.strip()

        return diffs
