from datetime import datetime

import util.cli_arg_parser as parser
from util.cli_arg_parser import BackendCommands
import tournament.main as tourney
import util.funcs
from config import configuration as cfg

import daemon.main as daemon


def main():
    command = parser.parse_backend_args()
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
        success, traces = daemon.make_report_request(datetime.now())

    elif command.type == BackendCommands.SHUTDOWN:
        success, traces = daemon.shutdown()

    elif command.type == BackendCommands.START_TOURNAMENT:
        if cfg.configuration_valid():
            success, traces = daemon.start()

    elif command.type == BackendCommands.CLOSE_SUBS:
        success, traces = daemon.close_submissions()

    else:
        traces = "Error: unrecognised command {}".format(command.type)

    print(traces)


if __name__ == "__main__":
    util.funcs.assert_python_version(3, 5, 2)
    main()
