
import socket
import json
import os
import subprocess

import cli.arg_parser as parser
from server.config import server_config


def start_server():
    """
    Spawn the server in a new process
    """
    print('starting server')
    path = os.path.dirname(os.path.abspath(__file__))
    # TODO determine how to ensure this is python 3.6
    subprocess.run("python --version", shell=True)
    process = subprocess.Popen(['python', path + '/start_server.py'], cwd=path)
    print('spawned process PID: {}'.format(process.pid))


def send_request(request: str):
    """
    Send a request to the request server. Print the received response
    :param request: The request sent to the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        try:
            sock.connect((server_config.get_host(), server_config.get_port()))
            sock.sendall(request.encode())

            # Receive data from the server and shut down
            received = sock.recv(1024).decode('utf-8')

            print('Sent:     {}'.format(request))
            print('Received: {}'.format(received))
            sock.close()

        except ConnectionRefusedError:
            print('Server not online')


if __name__ == "__main__":

    event = parser.parse_backend_args()
    if event.type == 'start_server':
        start_server()
    else:
        json = json.dumps(vars(event))
        send_request(json)

