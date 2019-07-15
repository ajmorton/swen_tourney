from enum import Enum


# inheriting from str allows for json to encode/decode between string and enum
class TestResult(str, Enum):
    TEST_PASSED = "TEST_PASSED"
    TEST_FAILED = "TEST_FAILED"
    TIMEOUT = "TIMEOUT"
    NOT_TESTED = "NOT TESTED"
