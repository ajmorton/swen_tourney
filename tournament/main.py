from tournament.configs.ant.AntConfig import AntConfig
import socket
from back_end.config import server_config
from typing import Tuple
import json


cfg = AntConfig()


def validate_tests(submission_dir: str) -> bool:
    cfg.prep_submission(submission_dir)
    (tests_valid, validation_traces) = cfg.validate_tests(submission_dir)
    write_file(submission_dir, "validate_tests_results.txt", validation_traces)
    return tests_valid


def validate_mutants(submission_dir: str) -> bool:
    cfg.prep_submission(submission_dir)
    (mutants_valid, validation_traces) = cfg.validate_mutants(submission_dir)
    write_file(submission_dir, "validate_mutants_results.txt", validation_traces)
    return mutants_valid


def submit(request) -> bool:
    submission_dir = request["dir"]
    (success, submission_traces) = send_request(request)
    write_file(submission_dir, "submission_results.txt", submission_traces)
    return success


def write_file(submission_dir: str, filename: str, contents: str):
    results_file = open(submission_dir + "/" + filename, "w")
    results_file.write(contents)
    results_file.close()


def send_request(request) -> Tuple[bool, str]:
    """
    Send a submission request to the request back_end.
    :param request: The request sent to the back_end. String
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
