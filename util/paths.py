import os
from datetime import datetime

import util.format as fmt
from util.types import Submitter, FilePath

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The list of submitters, and their emails, who are eligible to participate in the tournament
APPROVED_SUBMITTERS_LIST = root_dir + "/config/data/approved_submitters.json"

# Which assignment type the tournament is configured for
ASSIGNMENT_CONFIG = root_dir + "/config/data/assignment_config.json"

# The settings for emailing results to submitters. Email, password, smtp server details.
EMAIL_CONFIG = root_dir + "/config/data/email_config.json"

# the host and port of the request server
SERVER_CONFIG = root_dir + "/config/data/server_config.json"

# The file that stores the current state of the tournament
TOURNEY_STATE_FILE = root_dir + "/tournament/state/tourney_state.json"

# The directory to write tournament snapshots to
REPORT_DIR = root_dir + "/tournament/state"

# Trace file for tournament logs
TRACE_FILE = REPORT_DIR + "/tournament_log.txt"

# The python file to start up the request server
START_SERVER_FILE = root_dir + "/start_server.py"

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


def get_staged_report_request_filename(time: str) -> FilePath:
    dt = datetime.strptime(time, fmt.datetime_iso_string)
    return FilePath(STAGING_DIR + "/report_request_" + dt.strftime(fmt.datetime_file_string) + ".json")


def get_pre_validation_dir(submitter: Submitter) -> FilePath:
    return FilePath(PRE_VALIDATION_DIR + "/" + submitter)


def get_staging_dir(submitter: Submitter) -> FilePath:
    return FilePath(STAGING_DIR + "/" + submitter)


def get_tourney_dir(submitter: Submitter) -> FilePath:
    return FilePath(TOURNEY_DIR + "/" + submitter)


def get_snapshot_file_path(report_time: datetime):
    return REPORT_DIR + "/snapshot_" + report_time.strftime(fmt.datetime_file_string) + ".json"