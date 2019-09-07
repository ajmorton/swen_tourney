import sys
from datetime import datetime

from util import format as fmt
from util import paths


def assert_python_version(major: int, minor: int, micro: int):
    py_version = sys.version_info
    if py_version.major != major or py_version.minor != minor or py_version.micro != micro:
        print("ERROR: You are currently using Python {}.{}.{}".format(
            py_version.major, py_version.minor, py_version.micro)
        )
        print("Please run this program using Python {}.{}.{}".format(major, minor, micro))
        exit(1)


def timestamp() -> str:
    return datetime.now().strftime(fmt.datetime_trace_string) + " | "


def error() -> str:
    return datetime.now().strftime(fmt.datetime_trace_string) + " | ERROR: "


def print_tourney_trace(trace: str):
    with open(paths.TRACE_FILE, 'a') as file:
        file.write(timestamp() + trace + "\n")


def print_tourney_error(trace: str):
    with open(paths.TRACE_FILE, 'a') as file:
        file.write(error() + trace + "\n")
