from datetime import datetime

import cli.arg_parser as parser
from cli.arg_parser import BackendCommands
from server.request_types import AliveRequest, ReportRequest, ShutdownRequest
import server.main as server
import tournament.main as tourney
import cli.util
from config import configuration as cfg


def main():
    command = parser.parse_backend_args()

    if command.type == BackendCommands.CHECK_CONFIG:
        success, traces = cfg.check_configuration()

    elif command.type == BackendCommands.CLEAN:
        server_online, traces = server.send_request(AliveRequest())

        if server_online:
            traces = "Error: Server is currently online."\
                     "       Current submissions should not be removed unless the server is offline"
        else:
            tourney.clean()
            traces = "All submissions and tournament results have been deleted"

    elif command.type == BackendCommands.REPORT:
        success, traces = server.send_request(ReportRequest(command.email, datetime.now().isoformat()))

    elif command.type == BackendCommands.SHUTDOWN:
        success, traces = server.send_request(ShutdownRequest())

    elif command.type == BackendCommands.START_SERVER:
        success, traces = server.start_server()

    else:
        traces = "Error: unrecognised command {}".format(command.type)

    print(traces)


if __name__ == "__main__":
    cli.util.assert_python_version(3, 5, 2)
    main()
