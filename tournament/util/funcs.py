"""
Utility functions used by the tournament
"""

import sys
from datetime import datetime
from enum import Enum

from tournament.util import format as fmt, paths

class Ansi(str, Enum):
    """ANSI escape codes for coloured traces"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'

def assert_python_version():
    """ Assert that a minimum version of python is being run """
    min_py_version = (3, 8, 0)

    py_version = sys.version_info
    if py_version < min_py_version:
        print("ERROR: You are currently using Python {}.{}.{}".format(*py_version[0:3]))
        print("Please run this program using Python {}.{}.{} or greater".format(*min_py_version))
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
