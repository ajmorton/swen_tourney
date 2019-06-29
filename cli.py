import socket
import sys
import os
import subprocess
import time

from server import server_config

path = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = server_config.get_host(), server_config.get_port()


def start_server():
    """
    Spawn the request server in a new process
    """
    print('starting server')
    process = subprocess.Popen(['python', path + '/server/request_server.py'])
    print('spawned process PID: {}'.format(process.pid))


def send_request(request):
    """
    Send a request to the request server. Print the received response
    :param request: The request sent to the server. String
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        try:
            sock.connect((HOST, PORT))
            sock.sendall(request.encode())

            # Receive data from the server and shut down
            received = sock.recv(1024).decode('utf-8')

            print('Sent:     {}'.format(request))
            print('Received: {}'.format(received))
            sock.close()

        except ConnectionRefusedError:
            print('Server not online')


if __name__ == "__main__":
    args = ' '.join(sys.argv[1:])
    if args == 'start_server':
        start_server()
    else:
        send_request(args)

