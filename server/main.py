import json
import os
import socket
import subprocess
from typing import Tuple

from server.config import server_config
from server.request_types import *


def start_server() -> Tuple[bool, str]:
    """
    Spawn the server in a new process
    """
    print("Starting server")
    path = os.path.dirname(os.path.abspath(__file__))
    # TODO determine how to ensure this is python 3.7
    subprocess.run("python --version", shell=True)
    process = subprocess.Popen("python {}/../start_server.py".format(path), cwd=path, shell=True)
    print("Spawned process PID: {}".format(process.pid))

    return True, "Server started"


def send_request(request: ServerRequest) -> Tuple[bool, str]:
    """
    Send a submission request to the request server.
    :param request: The request sent to the server
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        request = json.dumps(request)

        try:
            sock.connect((server_config.get_host(), server_config.get_port()))
            sock.sendall(request.encode())

            received = sock.recv(1024).decode('utf-8')
            sock.close()

            if received == ServerResponse.SUBMISSION_SUCCESS:
                return True, "Submission successful"
            elif received == ServerResponse.ALIVE:
                return True, "Server is online"
            elif received == ServerResponse.REPORT_SUCCESS:
                return True, "Report is scheduled."
            elif received == ServerResponse.SERVER_SHUTDOWN:
                return True, "Server shutting down"
            else:
                return False, "An unknown error occurred"

        except ConnectionRefusedError:
            return False, "Error, the tournament server is not online.\nPlease contact a tutor and let them know."
