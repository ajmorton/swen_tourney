"""
Backend interface for the tournament. This is used for starting, stopping, and managing the tournament,
"""

from datetime import datetime
import time

from config import configuration as cfg
from daemon import flags
from daemon import main as daemon
from reporting import results_server
from tournament import main as tourney
from util import funcs
from util.cli_arg_parser import BackendCommands, parse_backend_args


def main():  # pylint: disable=too-many-branches
    """ Parse and process backend commands """
    command = parse_backend_args()
    traces = ""

    if command.type == BackendCommands.CHECK_CONFIG:
        cfg.configuration_valid()

    elif command.type == BackendCommands.CLEAN:
        server_online, traces = daemon.is_alive()

        if server_online:
            traces += "\nCurrent submissions should not be removed unless the server is offline"
        else:
            tourney.clean()
            traces = "All submissions and tournament results have been deleted"

    elif command.type == BackendCommands.REPORT:
        _, traces = daemon.make_report_request(datetime.now())

    elif command.type == BackendCommands.SHUTDOWN:
        _, traces = daemon.shutdown()

    elif command.type == BackendCommands.START_TOURNAMENT:

        tourney_already_online = flags.get_flag(flags.Flag.ALIVE)
        if tourney_already_online:
            traces = "Tournament already online."

        if not tourney_already_online and cfg.configuration_valid():

            success, traces = daemon.start()

            if success:
                time.sleep(1)
                _, results_server_traces = results_server.start_server()
                traces += "\n" + results_server_traces

    elif command.type == BackendCommands.CLOSE_SUBS:
        _, traces = daemon.close_submissions()

    elif command.type == BackendCommands.GET_DIFFS:
        _, traces = tourney.get_diffs()

    elif command.type == BackendCommands.RESCORE_INVALID:
        _, traces = tourney.rescore_invalid_progs()

    else:
        traces = "Error: unrecognised command {}".format(command.type)

    print(traces)


if __name__ == "__main__":
    funcs.assert_python_version(3, 5, 2)
    main()
