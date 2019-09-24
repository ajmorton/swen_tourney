"""
Backend interface for the tournament. This is used for starting, stopping, and managing the tournament,
"""

from datetime import datetime

from tournament.main import main as tourney
from tournament.config import configuration as cfg
from tournament.daemon import flags, main as daemon
from tournament.reporting import results_server
from tournament.util import BackendCommands, parse_backend_args
from tournament.util import funcs, Result


def start_tournament() -> Result:
    if flags.get_flag(flags.Flag.ALIVE):
        return Result(False, "Tournament already online")

    result = cfg.configuration_valid()
    if result:
        result += daemon.start()
        if result:
            result += results_server.start_server()
    return result


def clean() -> Result:
    result = daemon.is_alive()

    if result:
        return Result(False, result.traces + "Current submissions should not be removed unless the server is offline")

    tourney.clean()
    return Result(True, "All submissions and tournament results have been deleted")


def main():
    """ Parse and process backend commands """
    command = parse_backend_args()

    if command.type == BackendCommands.CHECK_CONFIG:
        result = cfg.configuration_valid()

    elif command.type == BackendCommands.CLEAN:
        result = clean()

    elif command.type == BackendCommands.REPORT:
        result = daemon.make_report_request(datetime.now())

    elif command.type == BackendCommands.SHUTDOWN:
        result = daemon.shutdown()

    elif command.type == BackendCommands.START_TOURNAMENT:
        result = start_tournament()

    elif command.type == BackendCommands.CLOSE_SUBS:
        result = daemon.close_submissions()

    elif command.type == BackendCommands.GET_DIFFS:
        result = tourney.get_diffs()

    elif command.type == BackendCommands.RESCORE_INVALID:
        result = tourney.rescore_invalid_progs()

    else:
        result = Result(False, "Error: unrecognised command {}".format(command.type))

    print(result.traces)
    exit(0 if result.success else 1)


if __name__ == "__main__":
    funcs.assert_python_version(3, 5, 2)
    main()
