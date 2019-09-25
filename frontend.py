"""
Frontend interface for the tournament. This is used to make submissions to the tournament.
"""
import os

import tournament.util.funcs
from tournament import util as parser
from tournament.util import FrontEndCommand
from tournament.util import Submitter, Result
import tournament.submission


def main():
    """
    Parse and process frontend commands
    """
    command = parser.parse_args()
    submission_dir = command.dir
    assg_name = os.path.basename(submission_dir.rstrip('/'))
    submitter = Submitter(os.path.basename((os.path.dirname(submission_dir).rstrip('/'))))

    result = Result(True, "\n==================================")

    if command.type == FrontEndCommand.CHECK_ELIGIBILITY:
        result += "Checking submitter eligibility  "
        result += tournament.submission.check_submitter_eligibility(submitter, assg_name)

    elif command.type == FrontEndCommand.COMPILE:
        result += "Preparing and compiling submission  "
        result += tournament.submission.compile_submission(submitter, submission_dir)

    elif command.type == FrontEndCommand.VALIDATE_TESTS:
        result += "Validating submitted tests    "
        result += tournament.submission.validate_tests(submitter)

    elif command.type == FrontEndCommand.VALIDATE_PROGS:
        result += "Validating submitted programs  "
        result += tournament.submission.validate_programs_under_test(submitter)

    elif command.type == FrontEndCommand.SUBMIT:
        result += "Validating submitted programs  "
        result += tournament.submission.make_submission(submitter)

    else:
        result += Result(False, "Error: unrecognised command: '{}'".format(command.type))

    result += "=================================="
    print(result.traces)

    exit(0 if result.success else 1)


if __name__ == "__main__":
    tournament.util.funcs.assert_python_version(3, 5, 2)
    main()
