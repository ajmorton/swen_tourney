"""
Common types used in the tournament
"""

from enum import Enum
from typing import NewType, Dict

FilePath = NewType("FilePath", str)
Submitter = NewType("Submitter", str)
Test = NewType("Test", str)
Prog = NewType("Prog", str)


# inheriting from str allows for json to encode/decode between string and enum
class TestResult(str, Enum):
    """ Results of running a test against a program """
    NO_BUGS_DETECTED = "NO_BUGS_DETECTED"
    BUG_FOUND = "BUG_FOUND"
    TIMEOUT = "TIMEOUT"
    NOT_TESTED = "NOT_TESTED"
    UNEXPECTED_RETURN_CODE = "UNEXPECTED_RETURN_CODE"


TestSet = NewType("TestSet", Dict[Submitter, Dict[Submitter, TestResult]])


class Result:
    def __init__(self, success: bool, trace: str):
        self.success = success
        self.traces = trace

    def __bool__(self):
        return self.success

    def __add__(self, other):
        if type(other) is str:
            return Result(self.success, self.traces + "\n" + other)
        else:
            return Result(self.success and other.success, self.traces + "\n" + other.traces)
