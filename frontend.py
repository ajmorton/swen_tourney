import cli.arg_parser as parser
import tournament.main as tourney
import os
import server.main as server
from server.request_types import SubmissionRequest
from cli.arg_parser import FrontEndCommand
from tournament.types.basetypes import Submitter
import cli.util


def main():
    """
    Parse and process frontend commands
    """
    command = parser.parse_frontend_args()

    if command.type == FrontEndCommand.CHECK_ELIGIBILITY:
        print()
        print("Checking submitter eligibility  ")
        print("==================================")
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, eligibility_check_traces = tourney.check_submitter_eligibility(submitter, submission_dir)
        print(eligibility_check_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.VALIDATE_TESTS:
        print()
        print("Validating submitted tests    ")
        print("==================================")

        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, validation_traces = tourney.validate_tests(submitter)
        print(validation_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.VALIDATE_PROGS:
        print()
        print("Validating submitted programs  ")
        print("==================================")
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        success, validation_traces = tourney.validate_programs_under_test(submitter)
        print(validation_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.SUBMIT:
        print()
        print("Validating submitted programs  ")
        print("==================================")
        submission_dir = command.dir
        submitter = Submitter(os.path.basename(submission_dir.rstrip('/')))
        tourney.write_submission_time(submitter)
        (success, submission_traces) = server.send_request(SubmissionRequest(submitter))
        print(submission_traces)
        print("==================================")
        print()

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
    cli.util.assert_python_version(3, 5, 2)
    main()
