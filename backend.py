"""
Backend interface for the tournament. This is used for starting, stopping, and managing the tournament,
"""

from tournament.cli_commands import parse_args
from tournament.util import funcs


if __name__ == "__main__":
    """ Parse and process backend commands """
    funcs.assert_python_version()

    args = parse_args(backend=True)
    result = args.func(args)

    print(result.traces)
    exit(0 if result.success else 1)
