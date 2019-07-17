import os

config_dir_path = os.path.dirname(os.path.abspath(__file__))
tournament_submissions_path = os.path.dirname(config_dir_path) + "/submissions"

SUBMITTERS_LIST = config_dir_path + "/approved_submitters.txt"
TOURNEY_STATE_FILE = config_dir_path + "/tourney_state.json"

PRE_VALIDATION_DIR = tournament_submissions_path + "/pre_validation"
STAGING_DIR = tournament_submissions_path + "/staged"
TOURNEY_DIR = tournament_submissions_path + "/tourney"
HEAD_TO_HEAD_DIR = tournament_submissions_path + "/head_to_head"

NEW_TESTS_FILE = "new_tests.json"
NEW_PROGS_FILE = "new_progs.json"
