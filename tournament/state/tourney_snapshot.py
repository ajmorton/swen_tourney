
from util.types import FilePath
from tournament.state.tourney_state import TourneyState
from datetime import datetime
import json
from config.configuration import AssignmentConfig
from util import format as fmt
from util import paths
from util.funcs import print_tourney_trace
import copy
import csv


class TourneySnapshot:

    NO_DATE = datetime.strftime(datetime.min, fmt.datetime_trace_string)

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

        self.snapshot = TourneySnapshot.default_snapshot

        if snapshot_file is not None:
            self.snapshot = json.load(open(snapshot_file, 'r'))
        elif report_time != datetime.min:
            self.create_snapshot_from_tourney_state(report_time)
            self.compute_normalised_scores()

    def write_snapshot(self, save_with_timestamp=False):
        json.dump(self.snapshot, open(paths.RESULTS_FILE, 'w'), indent=4, sort_keys=True)

        if save_with_timestamp:
            report_time = datetime.strptime(self.snapshot['snapshot_date'], fmt.datetime_trace_string)
            report_file_path = paths.get_snapshot_file_path(report_time)
            json.dump(self.snapshot, open(report_file_path, 'w'), indent=4, sort_keys=True)
            print_tourney_trace("Snapshot of tournament at {} written to {}".format(report_time, report_file_path))

    def write_csv(self):
        with open(paths.CSV_FILE, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            assg = AssignmentConfig().get_assignment()
            writer.writerow(["Student"] + assg.get_test_list() + assg.get_programs_list() +
                            ["normalised_bug_scores"] + ["normalised_prog_scores"])

            for (submitter, submitter_data) in sorted(self.snapshot['results'].items()):
                writer.writerow([submitter] +
                                [submitter_data["tests"][test] for test in sorted(submitter_data["tests"])] +
                                [submitter_data["progs"][prog] for prog in sorted(submitter_data["progs"])] +
                                [submitter_data["normalised_test_score"]] +
                                [submitter_data["normalised_prog_score"]])

    def create_snapshot_from_tourney_state(self, report_time: datetime):
        tourney_state = TourneyState()
        assg = AssignmentConfig().get_assignment()

        self.snapshot['num_submitters'] = len(tourney_state.get_valid_submitters())
        self.snapshot['snapshot_date'] = report_time.strftime(fmt.datetime_trace_string)

        for submitter in tourney_state.get_submitters():

            submitter_result = copy.deepcopy(TourneySnapshot.default_submitter_result)
            submitter_result['latest_submission_date'] = tourney_state.get_state()[submitter]['latest_submission_date']
            num_tests = tourney_state.get_num_tests(submitter)
            avg_num_tests = 1 if len(num_tests) == 0 else sum(num_tests.values()) / len(num_tests)
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

    def compute_normalised_scores(self):

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

    def set_time_to_process_last_submission(self, seconds: int):
        self.snapshot['time_to_process_last_submission'] = seconds

    def time_to_process_last_submission(self) -> int:
        return self.snapshot['time_to_process_last_submission']

    def date(self) -> datetime:
        return datetime.strptime(self.snapshot['snapshot_date'], fmt.datetime_trace_string)

    def num_submitters(self) -> int:
        return self.snapshot['num_submitters']

    def results(self) -> dict:
        return self.snapshot['results']
