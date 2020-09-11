"""
TourneySnapshot takes the state of the tournament at a point in time and processes the data to provide a summary.
This data can then be published.
"""

import copy
import csv
import json
from datetime import datetime

from tournament.config import AssignmentConfig
from tournament.processing.tourney_state import TourneyState
from tournament.util import FilePath
from tournament.util import format as fmt
from tournament.util import paths
from tournament.util.funcs import print_tourney_trace


class TourneySnapshot:
    """
    The TourneySnapshot class. Takes the state of the tournament and provides a processed summary of the data.
    """

    NO_DATE = datetime.strftime(datetime.min, fmt.DATETIME_TRACE_STRING)

    default_snapshot = {
        'snapshot_date': NO_DATE,
        'time_to_process_last_submission': 0,
        'num_submitters': 0,
        'results': {},
        'best_average_bugs_detected': 0.0,
        'best_average_tests_evaded': 0.0
    }

    default_submitter_result = {
        'latest_submission_date': NO_DATE,
        'tests': {},
        'progs': {},
        'average_tests_per_suite': 1.0,
        'average_bugs_detected': 0.0,
        'average_tests_evaded': 0.0,
        'normalised_test_score': 0,
        'normalised_prog_score': 0
    }

    def __init__(self, snapshot_file: FilePath = None, report_time: datetime = datetime.min):
        """
        __init__ takes one of snapshot_file or report_time as an argument.
        If snapshot_file is provided the snapshot is read from file.
        If report_time is provided then a new snapshot is created by processing the current tournament state.
        :param snapshot_file: the path of the offline file (if any) to read the snapshot from
        :param report_time: the time of the new snapshot to create
        """

        self.snapshot = TourneySnapshot.default_snapshot

        if snapshot_file is not None:
            self.snapshot = json.load(open(snapshot_file, 'r'))
        elif report_time != datetime.min:
            self._create_snapshot_from_tourney_state(report_time)
            self._compute_normalised_scores()
        else:
            raise NotImplementedError("Error: TourneySnapshot constructor must take one of {snapshot_file, datetime} "
                                      "as an argument")

    def write_snapshot(self):
        """ Write the snapshot to a json file """
        json.dump(self.snapshot, open(paths.RESULTS_FILE, 'w'), indent=4, sort_keys=True)

    def write_csv(self):
        """
        Write the snapshot details in a Blackboard friendly format. Only scoring details are provided in this file
        """
        with open(paths.CSV_FILE, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            assg = AssignmentConfig().get_assignment()
            writer.writerow(["Student"] + assg.get_test_list() + assg.get_programs_list() +
                            ["normalised_test_score"] + ["normalised_prog_score"] + ["total"] + ["total_rounded"])

            for (submitter, submitter_data) in sorted(self.snapshot['results'].items()):
                total_score = submitter_data["normalised_test_score"] + submitter_data["normalised_prog_score"]
                total_rounded = round(total_score * 2) / 2  # total score rounded to nearest 0.5
                writer.writerow([submitter] +
                                [submitter_data["tests"][test] for test in sorted(submitter_data["tests"])] +
                                [submitter_data["progs"][prog] for prog in sorted(submitter_data["progs"])] +
                                [submitter_data["normalised_test_score"]] +
                                [submitter_data["normalised_prog_score"]] +
                                [round(total_score, 2)] +
                                [total_rounded])

    def _create_snapshot_from_tourney_state(self, report_time: datetime):
        """
        Fetch the tournament state and process it to fill the TourneySnapshot object with useful metadata
        :param report_time: the time of the snapshot
        """
        tourney_state = TourneyState()
        assg = AssignmentConfig().get_assignment()

        self.snapshot['num_submitters'] = len(tourney_state.get_valid_submitters())
        self.snapshot['snapshot_date'] = report_time.strftime(fmt.DATETIME_TRACE_STRING)

        for submitter in tourney_state.get_submitters():

            submitter_result = copy.deepcopy(TourneySnapshot.default_submitter_result)
            submitter_result['latest_submission_date'] = tourney_state.get_state()[submitter]['latest_submission_date']
            num_tests = tourney_state.get_num_tests(submitter)
            avg_num_tests = 1 if not num_tests else sum(num_tests.values()) / len(num_tests)
            submitter_result['average_tests_per_suite'] = avg_num_tests

            total_bugs_detected = 0
            num_tests = len(assg.get_test_list())
            for test in assg.get_test_list():
                submitter_result['tests'][test] = tourney_state.get_bugs_detected(submitter, test)
                total_bugs_detected += submitter_result['tests'][test]
            submitter_result['average_bugs_detected'] = total_bugs_detected / float(num_tests)

            total_tests_evaded = 0
            num_progs = len(assg.get_programs_list())
            for prog in assg.get_programs_list():
                submitter_result['progs'][prog] = tourney_state.get_tests_evaded(submitter, prog)
                total_tests_evaded += submitter_result['progs'][prog]
            submitter_result['average_tests_evaded'] = total_tests_evaded / float(num_progs)

            self.snapshot['results'][submitter] = submitter_result

    def _compute_normalised_scores(self):
        """
        Determine the best prog and test scores of any submitter in the tournament, and normalise
        the scores of all other submitters against these best scores. Update submitters scores
        """

        results = self.snapshot['results']
        assg = AssignmentConfig().get_assignment()

        if results:
            self.snapshot['best_average_bugs_detected'] = \
                max([results[submitter]['average_bugs_detected'] for submitter in results])
            self.snapshot['best_average_tests_evaded'] = \
                max([results[submitter]['average_tests_evaded'] for submitter in results])

        for submitter in results.keys():
            submitter_bugs_detected = float(results[submitter]['average_bugs_detected'])
            submitter_tests_escaped = float(results[submitter]['average_tests_evaded'])

            results[submitter]['normalised_test_score'] = assg.compute_normalised_test_score(
                submitter_bugs_detected, self.snapshot['best_average_bugs_detected'],
                self.snapshot['results'][submitter]['average_tests_per_suite']
            )

            results[submitter]['normalised_prog_score'] = assg.compute_normalised_prog_score(
                submitter_tests_escaped, self.snapshot['best_average_tests_evaded']
            )

        # The current scoring algo for tests doesn't give the best test suite a maximums score.
        # re-normalise to make this happen
        best_test_score = max([results[submitter]['normalised_test_score'] for submitter in results.keys()])
        for submitter in results.keys():
            new_score = round(results[submitter]['normalised_test_score'] * (2.5 / best_test_score), 2)
            results[submitter]['normalised_test_score'] = new_score

    def set_time_to_process_last_submission(self, seconds: int):
        """ Set the time to process the last submission """
        self.snapshot['time_to_process_last_submission'] = seconds

    def time_to_process_last_submission(self) -> int:
        """ Get the time to process the last submission """
        return self.snapshot['time_to_process_last_submission']

    def date(self) -> datetime:
        """ The datetime of the snapshot """
        return datetime.strptime(self.snapshot['snapshot_date'], fmt.DATETIME_TRACE_STRING)

    def num_submitters(self) -> int:
        """
        The number of submitters who have made a valid submission in the tournament
        :return: The number of submitters who have made a valid submission in the tournament
        """
        return self.snapshot['num_submitters']

    def results(self) -> dict:
        """ The submitter results """
        return self.snapshot['results']
