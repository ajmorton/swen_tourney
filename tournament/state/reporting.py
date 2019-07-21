import json
import os
from datetime import datetime
from tournament.util.types.basetypes import *
from tournament.state.tourney_state import TourneyState
import tournament.config.paths as paths
import tournament.config.config as config
import emailer.emailer as emailer


def generate_report(time: datetime):
    tourney_state = TourneyState()

    report = {
        'report_date': report_time.isoformat(),
        'num_submitters': len(os.listdir(paths.TOURNEY_DIR)),
        'results': {}
    }

    for submitter in tourney_state.get_state().keys():
        submitter_result = {
            'email': tourney_state.get_state()[submitter]['email'],
            'latest_submission_date': tourney_state.get_state()[submitter]['latest_submission_date'],
            'tests': {},
            'progs': {},
            'average_bugs_detected': 0,
            'average_tests_escaped': 0,
            'normalised_test_score': 0,
            'normalised_prog_score': 0
        }

        total_bugs_detected = 0
        num_tests = len(config.assignment.get_test_list())
        for test in config.assignment.get_test_list():
            submitter_result['tests'][test] = tourney_state.get_bugs_detected(submitter, test)
            total_bugs_detected += submitter_result['tests'][test]
        submitter_result['average_bugs_detected'] = total_bugs_detected / float(num_tests)

        total_tests_evaded = 0
        num_progs = len(config.assignment.get_programs_list())
        for prog in config.assignment.get_programs_list():
            submitter_result['progs'][prog] = tourney_state.get_tests_evaded(submitter, prog)
            total_tests_evaded += submitter_result['progs'][prog]
        submitter_result['average_tests_escaped'] = total_tests_evaded / float(num_progs)

        report['results'][submitter] = submitter_result

    report_file_path = paths.REPORT_DIR + "/report_" + report_time.strftime(config.date_format) + ".json"

    json.dump(report, open(report_file_path, 'w'), indent=4)

    generate_normalised_scores(report_file_path)

    print("Report written to {}".format(report_file_path))


def generate_normalised_scores(report_file: FilePath):
    report = json.load(open(report_file, "r"))

    best_average_bugs_detected = 0.0
    best_average_tests_escaped = 0.0

    results = report['results']
    for submitter in results.keys():
        if results[submitter]['latest_submission_date'] is not None:
            if best_average_bugs_detected < results[submitter]['average_bugs_detected']:
                best_average_bugs_detected = results[submitter]['average_bugs_detected']
            if best_average_tests_escaped < results[submitter]['average_tests_escaped']:
                best_average_tests_escaped = results[submitter]['average_tests_escaped']

    for submitter in results.keys():
        submitter_bugs_detected = float(results[submitter]['average_bugs_detected'])
        submitter_tests_escaped = float(results[submitter]['average_tests_escaped'])

        results[submitter]['normalised_test_score'] = config.assignment.compute_normalised_test_score(
            submitter_bugs_detected, best_average_bugs_detected
        )

        results[submitter]['normalised_prog_score'] = config.assignment.compute_normalised_prog_score(
            submitter_tests_escaped, best_average_tests_escaped
        )

    json.dump(report, open(report_file, 'w'), indent=4)
