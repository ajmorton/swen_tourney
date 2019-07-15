import os

config_dir_path = os.path.dirname(os.path.abspath(__file__))
tournament_dir_path = os.path.dirname(config_dir_path)

SUBMITTERS_LIST = config_dir_path + "/approved_submitters.txt"
TOURNEY_STATE_FILE = config_dir_path + "/tourney_state.json"

STAGING_DIR = tournament_dir_path + "/submissions/staged"
TOURNEY_DIR = tournament_dir_path + "/submissions/tourney"
HEAD_TO_HEAD_DIR = tournament_dir_path + "/submissions/head_to_head"