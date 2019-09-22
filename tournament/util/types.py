"""
Common types used in the tournament
"""

from enum import Enum
from typing import NewType, Dict, Tuple

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
    COMPILATION_FAILED = "COMPILATION_FAILED"
    UNEXPECTED_RETURN_CODE = "UNEXPECTED_RETURN_CODE"


TestSet = NewType("TestSet", Dict[Submitter, Dict[Submitter, TestResult]])
Result = NewType("Result", Tuple[bool, str])
