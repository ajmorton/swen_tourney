import json
import os
from datetime import datetime
from tournament.util.types.basetypes import *
from tournament.state.tourney_state import TourneyState
import tournament.config.paths as paths
import tournament.config.config as config


def generate_report(time: datetime):
    tourney_state = TourneyState()

    report = {
        'report_date': time.isoformat(),
        'num_submitters': len(os.listdir(paths.TOURNEY_DIR)),
        'results': {}
    }

    for submitter in tourney_state.get_state().keys():
        submitter_result = {
            'email': tourney_state.get_state()[submitter]['email'],
            'latest_submission_date': tourney_state.get_state()[submitter]['latest_submission_date'],
            'tests': {},
            'progs': {},
            'total_bugs_detected': 0,
            'total_tests_escaped': 0,
            'normalised_test_score': 0,
            'normalised_prog_score': 0
        }

        total_test_score = 0
        for test in config.assignment.get_test_list():
            submitter_result['tests'][test] = tourney_state.get_bugs_detected(Submitter(submitter), test)
            total_test_score += submitter_result['tests'][test]
        submitter_result['total_bugs_detected'] = total_test_score

        total_prog_score = 0
        for prog in config.assignment.get_programs_list():
            submitter_result['progs'][prog] = tourney_state.get_tests_evaded(Submitter(submitter), prog)
            total_prog_score += submitter_result['progs'][prog]
        submitter_result['total_tests_escaped'] = total_prog_score

        report['results'][submitter] = submitter_result

    report_file_path = paths.REPORT_DIR + "/report_" + time.strftime(config.date_format) + ".json"

    json.dump(report, open(report_file_path, 'w'), indent=4)

    generate_normalised_scores(report_file_path)

    print("Report written to {}".format(report_file_path))


def generate_normalised_scores(report_file: FilePath):
    report = json.load(open(report_file, "r"))

    best_bugs_detected = 0
    best_tests_escaped = 0

    results = report['results']
    for submitter in results.keys():
        if results[submitter]['latest_submission_date'] is not None:
            if best_bugs_detected < results[submitter]['total_bugs_detected']:
                best_bugs_detected = results[submitter]['total_bugs_detected']
            if best_tests_escaped < results[submitter]['total_tests_escaped']:
                best_tests_escaped = results[submitter]['total_tests_escaped']

    for submitter in results.keys():
        submitter_bugs_detected = int(results[submitter]['total_bugs_detected'])
        submitter_tests_escaped = int(results[submitter]['total_tests_escaped'])

        results[submitter]['normalised_test_score'] = config.assignment.compute_normalised_test_score(
            submitter_bugs_detected, best_bugs_detected
        )

        results[submitter]['normalised_prog_score'] = config.assignment.compute_normalised_prog_score(
            submitter_tests_escaped, best_tests_escaped
        )

    json.dump(report, open(report_file, 'w'), indent=4)
