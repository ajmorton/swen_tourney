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


# The results of running a set of tests against a set of programs under test. e.g.
# TestSet = {
#   "test1": { "prog1": BUG_FOUND, "prog2": NO_BUGS_DETECTED },
#   "test2": { "prog1": BUG_FOUND, "prog2": BUG_FOUND }
# }
TestSet = NewType("TestSet", Dict[Test, Dict[Prog, TestResult]])


class Result:
    """ Contains both a boolean indicating success, and a traces string for additional detail """
    def __init__(self, success: bool, trace: str):
        self.success = success
        self.traces = trace

    def __bool__(self):
        return self.success

    def __add__(self, other):
        if isinstance(other, str):
            return Result(self.success, self.traces + "\n" + other)
        else:
            return Result(self.success and other.success, self.traces + "\n" + other.traces)
