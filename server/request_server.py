import socketserver
from event_processor import EventProcessor
from event_queue import EventQueue

import server_config


class TourneyRequestHandler(socketserver.BaseRequestHandler):
    """
    Handle request made to the Tourney server via the CLI and provide responses.
    """

    queue = EventQueue()

    def handle(self):
        """
        Handle a request made to the server.
        :return:
        """
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).decode()

        print('Request received: "{}"'.format(self.data))

        if self.data == "shutdown":
            self.request.sendall("SHUTTING_DOWN_SERVER".encode())
            self.server._BaseServer__shutdown_request = True

        elif self.data == 'get_port':
            self.request.sendall(str(server_config.get_port()).encode())
        elif self.data == 'get_host':
            self.request.sendall(str(server_config.get_host()).encode())
        else:
            # just send back the same data, but upper-cased
            self.queue.put(self.data)
            return_string = ", ".join(list(self.queue.queue))
            self.request.sendall(return_string.encode())


def start_server():
    """
    Create the EventProcessor and SocketServer threads
    """
    HOST, PORT = server_config.get_host(), server_config.get_port()
    try:
        # start up the  fifo dequeuer
        fifo_dequeuer = EventProcessor(TourneyRequestHandler.queue)
        fifo_dequeuer.start()

        # Create the server
        server = socketserver.TCPServer((HOST, PORT), TourneyRequestHandler)
        server.serve_forever()

        # when server stops serving, close all threads
        server.server_close()
        fifo_dequeuer.stop()

    except OSError as os_error:
        if os_error.errno == 48:
            # OSError 48: Socket address already in use
            # This occurs when the server is closed, and a restart is attempted
            # before the socket can be garbage collected
            print("Cannot allocate socket, already in use.")
            print("By default the server uses port", server_config.get_port(),
                  "on the loopback address", server_config.get_host(), ".")
            print("This resource can take some time to be freed when the "
                  "server is shutdown, try waiting a minute before running "
                  "again")

            fifo_dequeuer.stop()


if __name__ == "__main__":
    start_server()