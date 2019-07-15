import cli.arg_parser as parser
import tournament.main as tourney
import os
import socket
from server.config import server_config
from typing import Tuple, Dict
import json

from tournament.util.types.tourney_state import TourneyState
import tournament.util.funcs as funcs

def main():
    """
    Parse and process commands
    """
    event = parser.parse_frontend_args()
    event = vars(event)

    event_type = event['type']

    if event_type == "check_eligibility":
        submission_dir = event["dir"]
        submitter = os.path.basename(submission_dir.rstrip('/'))
        success = tourney.check_submitter_eligibility(submitter)

    elif event_type == "validate_tests":
        submission_dir = event['dir']
        success, validation_traces = tourney.validate_tests(submission_dir)
        write_file(submission_dir, "validate_tests_results.txt", validation_traces)

    elif event_type == "validate_progs":
        submission_dir = event['dir']
        success, validation_traces = tourney.validate_programs_under_test(submission_dir)
        write_file(submission_dir, "validate_tests_results.txt", validation_traces)

    elif event_type == "submit":
        submission_dir = event["dir"]
        submitter = os.path.basename(submission_dir.rstrip('/'))
        success = submit(submitter, submission_dir)

    else:
        success = False

    if success:
        exit(0)
    else:
        exit(1)


def submit(submitter: str, submission_dir: str) -> bool:
    request = {"type": "submit", "submitter": submitter, "dir": submission_dir}

    (success, submission_traces) = send_request(request)
    write_file(submission_dir, "submission_results.txt", submission_traces)
    return success


def write_file(submission_dir: str, filename: str, contents: str):
    results_file = open(submission_dir + "/" + filename, "w")
    results_file.write(contents)
    results_file.close()


def send_request(request: Dict[str, str]) -> Tuple[bool, str]:
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



if __name__ == "__main__":
    main()
