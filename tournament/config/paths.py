import os
from datetime import datetime
import tournament.config.config as config
from tournament.util.types.basetypes import Submitter, FilePath

config_dir_path = os.path.dirname(os.path.abspath(__file__))
tournament_submissions_path = os.path.dirname(config_dir_path) + "/submissions"

SUBMITTERS_LIST = config_dir_path + "/approved_submitters.json"
TOURNEY_STATE_FILE = config_dir_path + "/tourney_state.json"
REPORT_DIR = config_dir_path

PRE_VALIDATION_DIR = tournament_submissions_path + "/pre_validation"
STAGING_DIR = tournament_submissions_path + "/staged"
TOURNEY_DIR = tournament_submissions_path + "/tourney"
HEAD_TO_HEAD_DIR = tournament_submissions_path + "/head_to_head"

METADATA_FILE = "submission_metadata.json"
SUBMISSION_TIME = "submission_time.json"


def get_staged_report_request_filename(time: str) -> FilePath:
    dt = datetime.fromisoformat(time)
    return FilePath(STAGING_DIR + "/report_request_" + dt.strftime(config.date_format) + ".json")


def get_pre_validation_dir(submitter: Submitter) -> FilePath:
    return FilePath(PRE_VALIDATION_DIR + "/" + submitter)


def get_staging_dir(submitter: Submitter) -> FilePath:
    return FilePath(STAGING_DIR + "/" + submitter)


def get_tourney_dir(submitter: Submitter) -> FilePath:
    return FilePath(TOURNEY_DIR + "/" + submitter)
