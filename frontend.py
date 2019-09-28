"""
Frontend interface for the tournament. This is used to make submissions to the tournament.
"""
import tournament.util.funcs
from tournament.util.cli_arg_parser import parse_args
from tournament.util import Result
import tournament.submission


def main():
    """
    Parse and process frontend commands
    """

    result = Result(True, "\n==================================")
    args = parse_args()
    result += args.func(args)
    result += "=================================="

    print(result.traces)
    exit(0 if result.success else 1)


if __name__ == "__main__":
    tournament.util.funcs.assert_python_version(3, 5, 2)
    main()
