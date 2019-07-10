
from enum import Enum

class TestResult(Enum):
    TEST_PASSED = "TEST_PASSED"
    TEST_FAILED = "TEST_FAILED"
    TIMEOUT = "TIMEOUT"
