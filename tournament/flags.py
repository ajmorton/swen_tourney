"""
The TourneyDaemon handles state via flags in the file system. If a file is present the flag is considered to be true
"""
import os
import subprocess
from enum import Enum

from tournament.util import paths
from tournament.util.types import Result


class Flag(Enum):
    """ Flags written to the file system for the tournament to track state """


class TourneyFlag(Flag):
    """
    TourneyDaemon flags
        .alive: the TourneyDaemon is online
        .shutdown: the TourneyDaemon should shutdown on the next poll cycle
    """
    ALIVE = paths.STATE_DIR + "/.alive"
    SHUTDOWN = paths.STATE_DIR + "/.shutdown"


class SubmissionFlag(Flag):
    """
    SubmissionFlags
    Used to enforce an order between each of the testing stages. 'compile' must come directly after 'check_elig' etc.
        .elig: the submission has passed the 'check_elig' stage
        .compiled: the submission has passed the 'compile' stage
        .tests_valid: the submission has passed the 'validate_tests' stage
        .progs_valid: the submission has passed the 'validate_progs' stage
        .ready: the submission code is ready to be copied
    """
    ELIG = ".elig"
    COMPILED = ".compiled"
    TESTS_VALID = ".tests_valid"
    PROGS_VALID = ".progs_valid"
    SUBMISSION_READY = ".submission_ready"


def set_flag(flag: Flag, true: bool, submission: str = None, contents: str = ""):
    """
    Set a flag to true by creating it in the file system, or set it to false by deleting it from the file system.
    :param flag: the flag to set
    :param true: the value of the flag to set
    :param submission: the path of the submission to write the flag in, if applicable
    :param contents: An optional message to write inside the flag file
    """
    flag_path = flag.value if not submission else submission + "/" + flag.value

    if true:
        subprocess.run("touch {}".format(flag_path), shell=True, check=True)
        subprocess.run("echo '{}' > {}".format(contents, flag_path), shell=True, check=False)
    else:
        subprocess.run("rm -f {}".format(flag_path), shell=True, check=True)


def get_flag(flag: Flag, submission: str = None) -> Result:
    """
    Get the value of the provided flag
    :param flag: the flag to check
    :return: the value of the provided flag
    :param submission: the path of the submission to write the flag in, if applicable
    """
    flag_path = flag.value if not submission else submission + "/" + flag.value
    if os.path.exists(flag_path):
        return Result(True, open(flag_path, 'r').read().strip())
    else:
        return Result(False, "")


def clear_all_flags(submission: str = None):
    """ Delete all flags in the file system """
    if submission:
        for flag in SubmissionFlag:
            set_flag(flag, False, submission)
    else:
        for flag in TourneyFlag:
            set_flag(flag, False)
