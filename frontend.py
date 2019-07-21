import cli.arg_parser as parser
import tournament.main as tourney
import os
from tournament.util.types.basetypes import *
import server.main as server
from server.request_types import SubmissionRequest
from cli.arg_parser import FrontEndCommand


def main():
    """
    Parse and process frontend commands
    """
    command = parser.parse_frontend_args()

    if command.type == FrontEndCommand.CHECK_ELIGIBILITY:
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, eligibility_check_traces = tourney.check_submitter_eligibility(submitter, submission_dir)
        if os.path.isdir(submission_dir):
            write_file(submission_dir, "check_eligibility_results.txt", eligibility_check_traces)

    elif command.type == FrontEndCommand.VALIDATE_TESTS:
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, validation_traces = tourney.validate_tests(submitter)
        write_file(submission_dir, "validate_tests_results.txt", validation_traces)

    elif command.type == FrontEndCommand.VALIDATE_PROGS:
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, validation_traces = tourney.validate_programs_under_test(submitter)
        write_file(submission_dir, "validate_progs_results.txt", validation_traces)

    elif command.type == FrontEndCommand.SUBMIT:
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))

        tourney.write_submission_time(submitter)

        (success, submission_traces) = server.send_request(SubmissionRequest(submitter))
        write_file(submission_dir, "submission_results.txt", submission_traces)

    else:
        success = False

    if success:
        exit(0)
    else:
        exit(1)


def write_file(submission_dir: str, filename: str, contents: str):
    results_file = open(submission_dir + "/" + filename, 'w')
    results_file.write(contents)
    results_file.close()


if __name__ == "__main__":
    main()
