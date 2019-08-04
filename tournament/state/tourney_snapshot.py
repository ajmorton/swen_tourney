
from util.types import FilePath
from tournament.state.tourney_state import TourneyState
from datetime import datetime
import json
from config.configuration import AssignmentConfig
from util import format as fmt
from util import paths
from util.funcs import print_tourney_trace
import copy

assg = AssignmentConfig().get_assignment()


class TourneySnapshot:

    NO_DATE = datetime.strftime(datetime.min, fmt.datetime_trace_string)

    default_snapshot = {
        'snapshot_date': NO_DATE,
        'num_submitters': 0,
        'results': {},
        'best_average_bugs_detected': 0.0,
        'best_average_tests_evaded': 0.0
    }

    default_submitter_result = {
        'latest_submission_date': NO_DATE,
        'tests': {},
        'progs': {},
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

    def write_snapshot(self):
        report_time = datetime.strptime(self.snapshot['snapshot_date'], fmt.datetime_trace_string)
        report_file_path = paths.get_snapshot_file_path(report_time)
        json.dump(self.snapshot, open(report_file_path, 'w'), indent=4, sort_keys=True)
        json.dump(self.snapshot, open(paths.RESULTS_FILE, 'w'), indent=4, sort_keys=True)
        print_tourney_trace("Snapshot of tournament at {} written to {}".format(report_time, report_file_path))

    def create_snapshot_from_tourney_state(self, report_time: datetime):
        tourney_state = TourneyState()

        self.snapshot['num_submitters'] = len(tourney_state.get_valid_submitters())
        self.snapshot['snapshot_date'] = report_time.strftime(fmt.datetime_trace_string)

        for submitter in tourney_state.get_submitters():

            submitter_result = copy.deepcopy(TourneySnapshot.default_submitter_result)
            submitter_result['latest_submission_date'] = tourney_state.get_state()[submitter]['latest_submission_date']

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

        if results:
            self.snapshot['best_average_bugs_detected'] = \
                max([results[submitter]['average_bugs_detected'] for submitter in results])
            self.snapshot['best_average_tests_evaded'] = \
                max([results[submitter]['average_tests_evaded'] for submitter in results])

        for submitter in results.keys():
            submitter_bugs_detected = float(results[submitter]['average_bugs_detected'])
            submitter_tests_escaped = float(results[submitter]['average_tests_evaded'])

            results[submitter]['normalised_test_score'] = assg.compute_normalised_test_score(
                submitter_bugs_detected, self.snapshot['best_average_bugs_detected']
            )

            results[submitter]['normalised_prog_score'] = assg.compute_normalised_prog_score(
                submitter_tests_escaped, self.snapshot['best_average_tests_evaded']
            )

    def date(self) -> datetime:
        return datetime.strptime(self.snapshot['snapshot_date'], fmt.datetime_trace_string)

    def num_submitters(self) -> int:
        return self.snapshot['num_submitters']

    def results(self) -> dict:
        return self.snapshot['results']

    def best_average_bugs_detected(self) -> float:
        return self.snapshot['best_average_bugs_detected']

    def best_average_tests_evaded(self) -> float:
        return self.snapshot['best_average_tests_evaded']
