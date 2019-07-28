import socketserver
import json
from server.request_processor import RequestProcessor
from server.request_queue import RequestQueue
from server.request_types import *
from config.configs import ServerConfig


class TourneyRequestHandler(socketserver.BaseRequestHandler):
    """
    Handle request made to the Tourney server via the CLI and provide responses.
    """

    queue = RequestQueue()

    def handle(self):
        """
        Handle a request made to the server.
        :return:
        """
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).decode()
        req = request_from_json(json.loads(data))
        request_type = req.get_request_type()

        if request_type == RequestType.SHUTDOWN:
            self.server._BaseServer__shutdown_request = True
            self.request.sendall(ServerResponse.SERVER_SHUTDOWN.encode())
        elif request_type == RequestType.SUBMIT:
            print("Submission received from {}".format(req.submitter))
            self.queue.put(req)
            self.request.sendall(ServerResponse.SUBMISSION_SUCCESS.encode())
        elif request_type == RequestType.REPORT:
            self.queue.put(req)
            self.request.sendall(ServerResponse.REPORT_SUCCESS.encode())
        elif request_type == RequestType.ALIVE:
            self.request.sendall(ServerResponse.ALIVE.encode())
        else:
            print("Request type '{}' is not currently handled".format(request_type))


def start_server():
    """
    Create the RequestProcessor and SocketServer threads
    """
    server = ServerConfig()

    fifo_dequeuer = RequestProcessor(TourneyRequestHandler.queue)

    try:

        server = socketserver.TCPServer((server.host(), server.port()), TourneyRequestHandler)

        fifo_dequeuer.start()
        server.serve_forever()

        # when server stops serving, close all threads
        server.server_close()
        fifo_dequeuer.stop()

    except OSError as os_error:
        if os_error.errno in [48, 98]:
            # OSError 48: Socket address already in use
            # This occurs when the server is closed, and a restart is attempted
            # before the socket can be garbage collected
            print("Cannot allocate socket, already in use.")
            print("By default the server uses port {} on the loopback address {}.".format(server.port(), server.host()))
            print("This resource can take some time to be freed when the "
                  "server is shutdown, try waiting a minute before running "
                  "again")
        else:
            print("Unexpected OSError raised while starting server: {} {}".format(os_error.errno, os_error.strerror))

        fifo_dequeuer.stop()

