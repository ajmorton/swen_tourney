"""
File paths used by the tournament
"""

import os
from datetime import datetime

from tournament.util import format as fmt
from tournament.util.types import Submitter, FilePath

# The root of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The directory that contains all files that determine tournament state and configuration
STATE_DIR = ROOT_DIR + "/tournament/state"

# The directory that stores all config files
CONFIGS_DIR = STATE_DIR + "/config"

# Configuration files for the tournament
APPROVED_SUBMITTERS_LIST = CONFIGS_DIR + "/approved_submitters.json"
SUBMITTER_EXTENSIONS_LIST = CONFIGS_DIR + "/submitter_extensions.json"
ASSIGNMENT_CONFIG = CONFIGS_DIR + "/assignment_config.json"
SERVER_CONFIG = CONFIGS_DIR + "/server_config.json"
EMAIL_CONFIG = CONFIGS_DIR + "/email_config.json"

# Tournament state and snapshot used by the results server
TOURNEY_STATE_FILE = STATE_DIR + "/tourney_state.json"
RESULTS_FILE = STATE_DIR + "/tourney_results.json"

# Trace file for tournament logs
TRACE_FILE = ROOT_DIR + "/tournament_traces.log"

# Trace file for results server
RESULTS_SERVER_TRACE_FILE = ROOT_DIR + "/results_server_traces.log"

# CSV file for exporting tournament results
CSV_FILE = ROOT_DIR + "/student_results.csv"

# CSV file containing the diffs between the original source code and submitter progs
DIFF_FILE = ROOT_DIR + "/submitter_prog_diffs.csv"

# Track how many tests a submission has used per test suite
NUM_TESTS_FILE = "num_tests.json"

# Directories that store student submissions for validation, submission, and testing
SUBMISSIONS_DIR = STATE_DIR + "/submissions"
PRE_VALIDATION_DIR = SUBMISSIONS_DIR + "/pre_validation"
STAGING_DIR = SUBMISSIONS_DIR + "/staged"
TOURNEY_DIR = SUBMISSIONS_DIR + "/tourney"
HEAD_TO_HEAD_DIR = SUBMISSIONS_DIR + "/head_to_head"


def get_pre_validation_dir(submitter: Submitter) -> FilePath:
    """ Given a submitter, return the file path of their submission in the prevalidation directory """
    return FilePath(PRE_VALIDATION_DIR + "/" + submitter)


def get_tourney_dir(submitter: Submitter) -> FilePath:
    """ Given a submitter, return the file path of their submission in the tournament directory """
    return FilePath(TOURNEY_DIR + "/" + submitter)


def get_snapshot_file_path(report_time: datetime):
    """ Given a datetime, return a file path for a snapshot file with the datetime appended """
    return STATE_DIR + "/snapshot_" + report_time.strftime(fmt.DATETIME_FILE_STRING) + ".json"
