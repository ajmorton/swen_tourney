import socket
import sys
from server import server_config

HOST, PORT = server_config.get_host(), server_config.get_port()

data = " ".join(sys.argv[1:])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    try:
        sock.connect((HOST, PORT))
        sock.sendall(data.encode())

        # Receive data from the server and shut down
        received = sock.recv(1024).decode('utf-8')

        print('Sent:     {}'.format(data))
        print('Received: {}'.format(received))
        sock.close()

    except ConnectionRefusedError:
        print('Server not online')
