"""
The TourneyDaemon handles state via flags in the file system. If a file is present the flag is considered to be true
"""
import os
import subprocess
from enum import Enum

from tournament.util import paths


class Flag(Enum):
    """
    TourneyDaemon flags
        .alive: the TourneyDaemon is online
        .shutdown: the TourneyDaemon should shutdown on the next poll cycle
        .subs_closed: the tournament will no longer accept submissions
    """
    ALIVE = paths.STATE_DIR + "/.alive"
    SHUTTING_DOWN = paths.STATE_DIR + "/.shutdown"


def set_flag(flag: Flag, true: bool):
    """
    Set a flag to true by creating it in the file system, or set it to false by deleting it from the file system.
    :param flag: the flag to set
    :param true: the value of the flag to set
    """
    if true:
        subprocess.run("touch {}".format(flag.value), shell=True)
    else:
        subprocess.run("rm -f {}".format(flag.value), shell=True)


def get_flag(flag: Flag) -> bool:
    """
    Get the value of the provided flag
    :param flag: the flag to check
    :return: the value of the provided flag
    """
    return os.path.exists(flag.value)


def clear_all():
    """ Delete all flags in the file system """
    for flag in Flag:
        set_flag(flag, False)
