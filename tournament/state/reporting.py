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
            'submitted_date': tourney_state.get_state()[submitter]['latest_submission_date'],
            'tests': {},
            'progs': {},
            'total_test_score': 0,
            'total_prog_score': 0,
            'normalised_test_score': 0,
            'normalised_prog_score': 0
        }

        total_test_score = 0
        for test in config.assignment.get_test_list():
            submitter_result['tests'][test] = tourney_state.get_bugs_detected(Submitter(submitter), test)
            total_test_score += submitter_result['tests'][test]
        submitter_result['total_test_score'] = total_test_score

        total_prog_score = 0
        for prog in config.assignment.get_programs_list():
            submitter_result['progs'][prog] = tourney_state.get_tests_evaded(Submitter(submitter), prog)
            total_prog_score += submitter_result['progs'][prog]
        submitter_result['total_prog_score'] = total_prog_score

        report['results'][submitter] = submitter_result

    report_file_path = paths.REPORT_DIR + "/report_" + time.strftime(config.date_format) + ".json"

    with open(report_file_path, 'w') as outfile:
        json.dump(report, outfile, indent=4)

    print("Report written to {}".format(report_file_path))
