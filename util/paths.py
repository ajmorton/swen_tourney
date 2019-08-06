import os
from datetime import datetime

import util.format as fmt
from util.types import Submitter, FilePath

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The list of submitters who are eligible to participate in the tournament
APPROVED_SUBMITTERS_LIST = root_dir + "/config/data/approved_submitters.json"

# Which assignment type the tournament is configured for
ASSIGNMENT_CONFIG = root_dir + "/config/data/assignment_config.json"

# the host and port of the request server
SERVER_CONFIG = root_dir + "/config/data/server_config.json"

# the config for sending emails
EMAIL_CONFIG = root_dir + "/config/data/email_config.json"

# The file that stores the current state of the tournament
TOURNEY_STATE_FILE = root_dir + "/tournament/state/tourney_state.json"

# The directory to write tournament snapshots to
REPORT_DIR = root_dir + "/tournament/state"

# Trace file for tournament logs
TRACE_FILE = REPORT_DIR + "/tournament_log.txt"

# Snapshot used by the results server
RESULTS_FILE = REPORT_DIR + "/tourney_results.json"

# The python file to start up the tournament daemon
START_DAEMON_FILE = root_dir + "/start_daemon.py"

# The python file to start up the results server
START_RESULTS_SERVER_FILE = root_dir + "/start_results_server.py"

# The root of the project
ROOT_DIR = root_dir

# Directories that store student submissions for validation, submission, and testing
tournament_submissions_path = root_dir + "/tournament/submissions"
PRE_VALIDATION_DIR = tournament_submissions_path + "/pre_validation"
STAGING_DIR = tournament_submissions_path + "/staged"
TOURNEY_DIR = tournament_submissions_path + "/tourney"
HEAD_TO_HEAD_DIR = tournament_submissions_path + "/head_to_head"

# Metadata files with additional information about submissions. These are created for each submission
METADATA_FILE = "submission_metadata.json"
SUBMISSION_TIME = "submission_time.json"


def get_pre_validation_dir(submitter: Submitter) -> FilePath:
    return FilePath(PRE_VALIDATION_DIR + "/" + submitter)


def get_staging_dir(submitter: Submitter) -> FilePath:
    return FilePath(STAGING_DIR + "/" + submitter)


def get_tourney_dir(submitter: Submitter) -> FilePath:
    return FilePath(TOURNEY_DIR + "/" + submitter)


def get_snapshot_file_path(report_time: datetime):
    return REPORT_DIR + "/snapshot_" + report_time.strftime(fmt.datetime_file_string) + ".json"
