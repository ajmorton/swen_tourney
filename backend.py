"""
Backend interface for the tournament. This is used for starting, stopping, and managing the tournament,
"""

from tournament.util.cli_arg_parser import parse_args
from tournament.util import funcs


def main():
    """ Parse and process backend commands """
    args = parse_args(backend=True)
    result = args.func(args)

    print(result.traces)
    exit(0 if result.success else 1)


if __name__ == "__main__":
    funcs.assert_python_version(3, 5, 2)
    main()
