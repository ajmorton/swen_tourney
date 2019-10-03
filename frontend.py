"""
Frontend interface for the tournament. This is used to make submissions to the tournament.
"""
import tournament.util.funcs
from tournament.cli_commands import parse_args
from tournament.util import Result
import tournament.submission_validation


if __name__ == "__main__":
    """
    Parse and process frontend commands
    """
    tournament.util.funcs.assert_python_version()

    result = Result(True, "\n==================================")
    args = parse_args()
    result += args.func(args)
    result += "=================================="

    print(result.traces)
    exit(0 if result.success else 1)
