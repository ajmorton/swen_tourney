from datetime import datetime
import json
import socket
import subprocess
from util.types import Result
from util import paths
from config.configuration import ServerConfig
from server.request_types import *
import util.format as fmt


def start_server() -> Result:
    """
    Spawn the server in a new process
    """
    subprocess.Popen("python3 {}".format(paths.START_SERVER_FILE), cwd=paths.ROOT_DIR, shell=True)

    return Result((True, "Server starting.\nTraces are being written to {}".format(paths.TRACE_FILE)))


def send_request(request: ServerRequest) -> Result:
    """
    Send a submission request to the request server.
    :param request: The request sent to the server
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        request = json.dumps(request)
        server = ServerConfig()

        try:
            sock.connect((server.host(), server.port()))
            sock.sendall(request.encode())

            received = sock.recv(1024).decode('utf-8')
            sock.close()

            if received == ServerResponse.SUBMISSION_SUCCESS:
                result, trace = True, "Submission successfully made at {}".format(
                    datetime.now().strftime(fmt.datetime_trace_string))
            elif received == ServerResponse.ALIVE:
                result, trace = True, "Server is online"
            elif received == ServerResponse.REPORT_SUCCESS:
                result, trace = True, "Report is scheduled."
            elif received == ServerResponse.SERVER_SHUTDOWN:
                result, trace = True, "Server shutting down"
            else:
                result, trace = False, "An unknown error occurred"

            return Result((result, trace))
        except ConnectionRefusedError:
            return Result(
                (False, "Error, the tournament server is not online.\nPlease contact a tutor and let them know.")
            )
