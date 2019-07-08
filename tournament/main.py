from tournament.configs.ant.AntConfig import AntConfig
import socket
from server.config import server_config
from typing import Tuple
import json
from tournament.util.types import TestResult


cfg = AntConfig()


def validate_tests(submission_dir: str) -> bool:
    cfg.prep_submission(submission_dir)

    tests_valid = True
    validation_traces = "Validation results:"
    for test in cfg.get_test_list():
        test_result = cfg.run_test(test, "original", submission_dir)

        if test_result == TestResult.TIMEOUT:
            validation_traces += "\n{} {} test FAIL - Timeout".format("original", test)
        elif test_result == TestResult.TEST_PASSED:
            validation_traces += "\n{} {} test SUCCESS - No bugs detected in original program".format("original", test)
        elif test_result == TestResult.TEST_FAILED:
            validation_traces += "\n{} {} test FAIL - Test falsely reports an error in original code".format("original", test)
        else:
            validation_traces += "\n{} {} ERROR - unexpected test result: {}".format("original", test, test_result)

        tests_valid = tests_valid and test_result == TestResult.TEST_PASSED

    write_file(submission_dir, "validate_tests_results.txt", validation_traces)
    return tests_valid


def validate_programs_under_test(submission_dir: str) -> bool:
    cfg.prep_submission(submission_dir)

    puts_valid = True
    validation_traces = "Validation results:"

    for put in cfg.get_programs_under_test_list():
        for test in cfg.get_test_list():
            test_result = cfg.run_test(test, put, submission_dir)

            if test_result == TestResult.TIMEOUT:
                validation_traces += "\n{} {} test FAIL - Timeout".format(put, test)
            elif test_result == TestResult.TEST_PASSED:
                validation_traces += "\n{} {} test FAIL - Test suite does not detect error".format(put, test)
            elif test_result == TestResult.TEST_FAILED:
                validation_traces += "\n{} {} test SUCCESS - Test suite detects error".format(put, test)
            else:
                validation_traces += "\n{} {} ERROR - unexpected test result: {}".format(put, test, test_result)

            puts_valid = puts_valid and test_result == TestResult.TEST_FAILED

    write_file(submission_dir, "validate_tests_results.txt", validation_traces)
    return puts_valid


def submit(submitter, submission_dir) -> bool:
    request = {"type": "submit", "submitter": submitter, "dir": submission_dir}

    (success, submission_traces) = send_request(request)
    write_file(submission_dir, "submission_results.txt", submission_traces)
    return success


def write_file(submission_dir: str, filename: str, contents: str):
    results_file = open(submission_dir + "/" + filename, "w")
    results_file.write(contents)
    results_file.close()


def send_request(request) -> Tuple[bool, str]:
    """
    Send a submission request to the request server.
    :param request: The request sent to the server. String
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        request = json.dumps(request)

        try:
            sock.connect((server_config.get_host(), server_config.get_port()))
            print('Sending: {}'.format(request))
            sock.sendall(request.encode())

            received = sock.recv(1024).decode('utf-8')
            sock.close()

            if received == "SUBMISSION_SUCCESSFUL":
                return True, "Submission successful"
            else:
                return False, "An unknown error occurred"

        except ConnectionRefusedError:

            print('Server not online')
            return False, "Error, the tournament server is not online.\nPlease contact a tutor and let them know."
