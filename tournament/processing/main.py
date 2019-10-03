"""
The core functions used for running the tournament
"""
import csv
import json
import os
import subprocess
from datetime import datetime
from functools import partial
from multiprocessing import current_process, Pool
from typing import Tuple

from tournament.config import AssignmentConfig
from tournament.daemon import flags
from tournament.processing.tourney_snapshot import TourneySnapshot
from tournament.processing.tourney_state import TourneyState
from tournament.util import Prog, Result, Submitter, Test, TestSet
from tournament.util import paths, print_tourney_trace


def run_submission(submitter: Submitter, submission_time: str, new_tests: [Test], new_progs: [Prog], pool: Pool):
    """
    Run a submission against all other previously made submissions in the tournament.
    The submission has been compared against the submitters prior submission (if any). Only new tests and progs require
    retesting
    :param submitter: the submitter
    :param submission_time: the time of the new submission
    :param new_tests: the list of new tests that need to be run/rerun
    :param new_progs: the list of new programs that need to be run/rerun
    :param pool: the thread pool to use for testing in parallel
    """

    tourney_state = TourneyState()
    other_submitters = [sub for sub in tourney_state.get_valid_submitters() if sub != submitter]

    print_tourney_trace("Processing submission for {}.".format(submitter))
    print_tourney_trace("\tNew tests: {}".format(new_tests))
    print_tourney_trace("\tNew progs: {}".format(new_progs))

    tourney_state.set_time_of_submission(submitter, submission_time)
    num_tests = json.load(open(paths.get_tourney_dir(submitter) + "/" + paths.NUM_TESTS_FILE, 'r'))
    tourney_state.set_number_of_tests(submitter, num_tests)

    # multiprocessing.Pool.map can only work on one argument, use functools.partial to curry
    # run_tests into functions with just one argument
    rt_new_tests = partial(run_tests, tourney_state=tourney_state, new_tests=new_tests, new_progs=[])
    rt_new_progs = partial(run_tests, tourney_state=tourney_state, new_tests=[], new_progs=new_progs)

    # run submitter tests against others progs
    tester_results = pool.map(rt_new_tests, [(submitter, other) for other in other_submitters])

    # run others tests against submitters progs
    testee_results = pool.map(rt_new_progs, [(other, submitter) for other in other_submitters])

    for (tester, testee, test_set) in tester_results + testee_results:
        tourney_state.set(tester, testee, test_set)

    print_tourney_trace("Submission from {} tested".format(submitter))
    tourney_state.save_to_file()


def run_tests(pair: Tuple[Submitter, Submitter], tourney_state: TourneyState, new_tests: [Test], new_progs: [Prog]
              ) -> [Submitter, Submitter, TestSet]:
    """
    Provided a tester/testee pair, run the testers tests against the testees programs.
    If a test or a program is marked as new then run the test against the program, otherwise the values can be taken
    from the existing tournament state
    :param pair: the tester/testee pair
    :param tourney_state: the existing tournament state
    :param new_tests: the list of new tests that need to be run
    :param new_progs: the list of new programs that need to be tested
    :return: (tester, testee, results of running all tests against all programs)
    """

    assg = AssignmentConfig().get_assignment()

    test_stage_dir = paths.HEAD_TO_HEAD_DIR + "/test_stage_" + current_process().name
    if not os.path.isdir(test_stage_dir):
        subprocess.run("cp -rf {} {}".format(assg.get_source_assg_dir(), test_stage_dir), shell=True)

    (tester, testee) = pair

    assg.prep_test_stage(tester, testee, test_stage_dir)
    test_set = {}
    for test in assg.get_test_list():
        test_set[test] = {}
        for prog in assg.get_programs_list():
            if test in new_tests or prog in new_progs:
                test_set[test][prog], _ = assg.run_test(test, prog, test_stage_dir)
            else:
                # no need to rerun this test, keep the results from the current tournament state
                test_set[test][prog] = tourney_state.get(tester, testee, test, prog)

    return tester, testee, test_set


def get_diffs() -> Result:
    """
    Print to paths.DIFF_FILE the changes each submitter made in their programs compared to the original program.
    """

    assg = AssignmentConfig().get_assignment()
    tourney_results = json.load(open(paths.RESULTS_FILE, 'r'))

    csv_columns = ["submitter", "mutant", "num_tests_evaded", "diff", "invalid?"]
    diff_csv = csv.DictWriter(open(paths.DIFF_FILE, 'w'), fieldnames=csv_columns)
    diff_csv.writeheader()

    diffs = []
    for submitter in os.listdir(paths.TOURNEY_DIR):
        submitter_diffs = assg.get_diffs(paths.get_tourney_dir(Submitter(submitter)))
        for prog in sorted(submitter_diffs.keys()):
            num_tests_evaded = tourney_results['results'][submitter]['progs'][prog]
            diffs.append({'submitter': submitter, 'mutant': prog, 'num_tests_evaded': num_tests_evaded,
                          'diff': submitter_diffs[prog], 'invalid?': ""})

    # sort by num_tests_evaded, the most successful programs will be at the top of the csv file and
    # are prioritised for inspection
    for entry in sorted(diffs, key=lambda e: e['num_tests_evaded'], reverse=True):
        diff_csv.writerow(entry)

    invalid = ["Y", "y", "True", "true", "X", "x"]
    valid = ["N", "n", ""]

    return Result(True, "\nDiff file has been created at: {}.\n"
                        "Invalid entries should be marked with one of {} in the 'invalid?' column, "
                        "valid entries can be marked with one of {}.".format(paths.DIFF_FILE, invalid, valid))


def rescore_invalid_progs() -> Result:
    """
    Read from the diff file which submitted progs are invalid, and give those programs a score of zero in
    the tournament state
    """

    diff_csv = csv.DictReader(open(paths.DIFF_FILE, 'r'))
    tourney_state = TourneyState()

    invalid = ["Y", "y", "True", "true", "X", "x"]
    valid = ["N", "n", ""]

    num_invalid_progs = 0
    parsing_results = Result(True, "")
    for row in diff_csv:
        is_invalid, sub, mut = row['invalid?'], row['submitter'], row['mutant']
        if is_invalid in invalid:
            tourney_state.invalidate_prog(sub, mut)
            num_invalid_progs += 1
        elif is_invalid in valid:
            continue
        else:
            parsing_results += Result(False, "Error: unrecognised value '{}' in the 'invalid?' column for {} {}."
                                      .format(is_invalid, sub, mut))

    if not parsing_results:
        return Result(False, parsing_results.traces +
                      "\nUnrecognised values in the 'invalid?' column of {} have been detected. "
                      "Please use one of {} for valid entries, or one of {} for invalid entries"
                      .format(paths.DIFF_FILE, valid, invalid))

    # update tourney state and results
    parsing_results.traces += "Results updated. Recalculating submitter scores."
    tourney_state.save_to_file()
    TourneySnapshot(report_time=datetime.now()).write_snapshot()

    return Result(True, "{} invalid programs have had their score set to zero".format(num_invalid_progs))


def clean():
    """
    Remove all submissions and reset the tourney state
    """
    subprocess.run("rm -rf {}".format(paths.PRE_VALIDATION_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.STAGING_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.TOURNEY_DIR + "/*"), shell=True)
    subprocess.run("rm -rf {}".format(paths.HEAD_TO_HEAD_DIR + "/*"), shell=True)
    subprocess.run("rm -f  {}".format(paths.TOURNEY_STATE_FILE), shell=True)
    subprocess.run("rm -f  {}".format(paths.TRACE_FILE), shell=True)
    subprocess.run("rm -f  {}".format(paths.RESULTS_FILE), shell=True)
    subprocess.run("rm -f  {}/snapshot*.json".format(paths.STATE_DIR), shell=True)
    subprocess.run("rm -f  {}".format(paths.ASSIGNMENT_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.APPROVED_SUBMITTERS_LIST), shell=True)
    subprocess.run("rm -f  {}".format(paths.SERVER_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.EMAIL_CONFIG), shell=True)
    subprocess.run("rm -f  {}".format(paths.SUBMITTER_EXTENSIONS_LIST), shell=True)
    subprocess.run("rm -f  {}".format(paths.DIFF_FILE), shell=True)
    flags.clear_all()
