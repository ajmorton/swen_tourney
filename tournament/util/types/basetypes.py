from enum import Enum
from typing import NewType, Dict

FilePath = NewType("FilePath", str)
Submitter = NewType("Submitter", str)
Test = NewType("Test", str)
Prog = NewType("Prog", str)


# inheriting from str allows for json to encode/decode between string and enum
class TestResult(str, Enum):
    NO_BUGS_DETECTED = "NO_BUGS_DETECTED"
    BUG_FOUND = "BUG_FOUND"
    TIMEOUT = "TIMEOUT"
    NOT_TESTED = "NOT TESTED"


TestSet = NewType("TestSet", Dict[Submitter, Dict[Submitter, TestResult]])
