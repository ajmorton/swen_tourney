"""
Utility functions used by the tournament
"""

import sys
from datetime import datetime

from tournament.util import format as fmt
from tournament.util import paths


def assert_python_version(major: int, minor: int, micro: int):
    """ Assert that a specific version of python is being run """
    py_version = sys.version_info
    if py_version.major != major or py_version.minor != minor or py_version.micro != micro:
        print("ERROR: You are currently using Python {}.{}.{}".format(
            py_version.major, py_version.minor, py_version.micro))
        print("Please run this program using Python {}.{}.{}".format(major, minor, micro))
        exit(1)


def timestamp() -> str:
    """ Return a timestamp prefix for tournament traces """
    return datetime.now().strftime(fmt.DATETIME_TRACE_STRING) + " | "


def error() -> str:
    """ Return a timestamp prefix for tournament error traces """
    return datetime.now().strftime(fmt.DATETIME_TRACE_STRING) + " | ERROR: "


def print_tourney_trace(trace: str):
    """ Write tournament traces to the log file """
    with open(paths.TRACE_FILE, 'a') as file:
        file.write(timestamp() + trace + "\n")


def print_tourney_error(trace: str):
    """ Write tournament error traces to the log file """
    with open(paths.TRACE_FILE, 'a') as file:
        file.write(error() + trace + "\n")
