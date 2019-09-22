"""
Frontend interface for the tournament. This is used to make submissions to the tournament.
"""
import os

import tournament.main as tourney
import tournament.util.funcs
from tournament import util as parser, daemon as daemon
from tournament.util import FrontEndCommand
from tournament.util import Submitter


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
        assg_name = os.path.basename(submission_dir.rstrip('/'))
        submitter = Submitter(os.path.basename((os.path.dirname(submission_dir).rstrip('/'))))
        success, eligibility_check_traces = tourney.check_submitter_eligibility(submitter, assg_name, submission_dir)
        print(eligibility_check_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.VALIDATE_TESTS:
        print()
        print("Validating submitted tests    ")
        print("==================================")
        submitter = Submitter(os.path.basename((os.path.dirname(command.dir).rstrip('/'))))
        success, validation_traces = tourney.validate_tests(submitter)
        print(validation_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.VALIDATE_PROGS:
        print()
        print("Validating submitted programs  ")
        print("==================================")
        submitter = Submitter(os.path.basename((os.path.dirname(command.dir).rstrip('/'))))
        success, validation_traces = tourney.validate_programs_under_test(submitter)
        print(validation_traces)
        print("==================================")
        print()

    elif command.type == FrontEndCommand.SUBMIT:
        print()
        print("Validating submitted programs  ")
        print("==================================")
        submitter = Submitter(os.path.basename((os.path.dirname(command.dir).rstrip('/'))))
        (success, submission_traces) = daemon.make_submission(submitter)
        print(submission_traces)
        print()
        print("Check the status of the tournament at http://murray.cis.unimelb.edu.au:8080/")
        print("==================================")
        print()

    else:
        success = False

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    tournament.util.funcs.assert_python_version(3, 5, 2)
    main()
