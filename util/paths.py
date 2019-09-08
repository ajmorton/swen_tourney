"""
File paths used by the tournament
"""

import os
from datetime import datetime

import util.format as fmt
from util.types import Submitter, FilePath

# The root of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The list of submitters who are eligible to participate in the tournament
APPROVED_SUBMITTERS_LIST = ROOT_DIR + "/config/data/approved_submitters.json"

# Which assignment type the tournament is configured for
ASSIGNMENT_CONFIG = ROOT_DIR + "/config/data/assignment_config.json"

# the host and port of the request server
SERVER_CONFIG = ROOT_DIR + "/config/data/server_config.json"

# the config for sending emails
EMAIL_CONFIG = ROOT_DIR + "/config/data/email_config.json"

# The file that stores the current state of the tournament
TOURNEY_STATE_FILE = ROOT_DIR + "/tournament/state/tourney_state.json"

# The directory to write tournament snapshots to
REPORT_DIR = ROOT_DIR + "/tournament/state"

# Snapshot used by the results server
RESULTS_FILE = REPORT_DIR + "/tourney_results.json"

# Trace file for tournament logs
TRACE_FILE = ROOT_DIR + "/tournament_traces.log"

# CSV file for exporting tournament results
CSV_FILE = ROOT_DIR + "/student_results.csv"

# CSV file containing the diffs between the original source code and submitter progs
DIFF_FILE = ROOT_DIR + "/submitter_prog_diffs.csv"

# Track how many tests a submission has used per test suite
NUM_TESTS_FILE = "num_tests.json"

# Directories that store student submissions for validation, submission, and testing
SUBMISSIONS_PATH = ROOT_DIR + "/tournament/submissions"
PRE_VALIDATION_DIR = SUBMISSIONS_PATH + "/pre_validation"
STAGING_DIR = SUBMISSIONS_PATH + "/staged"
TOURNEY_DIR = SUBMISSIONS_PATH + "/tourney"
HEAD_TO_HEAD_DIR = SUBMISSIONS_PATH + "/head_to_head"


def get_pre_validation_dir(submitter: Submitter) -> FilePath:
    """ Given a submitter, return the file path of their submission in the prevalidation directory """
    return FilePath(PRE_VALIDATION_DIR + "/" + submitter)


def get_tourney_dir(submitter: Submitter) -> FilePath:
    """ Given a submitter, return the file path of their submission in the tournament directory """
    return FilePath(TOURNEY_DIR + "/" + submitter)


def get_snapshot_file_path(report_time: datetime):
    """ Given a datetime, return a file path for a snapshot file with the datetime appended """
    return REPORT_DIR + "/snapshot_" + report_time.strftime(fmt.DATETIME_FILE_STRING) + ".json"
