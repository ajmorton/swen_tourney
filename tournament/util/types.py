
from enum import Enum
import os


class TestResult(Enum):
    TEST_PASSED = "TEST_PASSED"
    TEST_FAILED = "TEST_FAILED"
    TIMEOUT = "TIMEOUT"


SUBMITTERS_LIST = os.path.dirname(os.path.abspath(__file__)) + "/../data/approved_submitters.txt"
