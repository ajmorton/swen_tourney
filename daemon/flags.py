import os
import subprocess
from enum import Enum

from util import paths
from util.types import FilePath


class Flag(Enum):
    ALIVE = paths.REPORT_DIR + "/.alive"
    SHUTTING_DOWN = paths.REPORT_DIR + "/.shutdown"
    SUBMISSIONS_CLOSED = paths.REPORT_DIR + "/.subs_closed"


def set_flag(flag: Flag, true: bool):
    if true:
        subprocess.run("touch {}".format(flag.value), shell=True)
    else:
        subprocess.run("rm -f {}".format(flag.value), shell=True)


def get_flag(flag: Flag) -> bool:
    return os.path.exists(flag.value)


# There are two threads that copy submissions to and from the STAGING dir respectively.
# Use this flag to prevent the copying of partially copied submissions
READY_FLAG = "/.ready"


def set_submission_ready(submission_dir: FilePath):
    subprocess.run("touch {}".format(submission_dir + READY_FLAG), shell=True)


def submission_ready(submission_dir: FilePath) -> bool:
    return os.path.exists(submission_dir + READY_FLAG)


def clear_all():
    for flag in Flag:
        set_flag(flag, False)
