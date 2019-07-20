import socketserver
import json
from server.request_processor import RequestProcessor
from server.request_queue import RequestQueue
from server.config import server_config
from server.request_types import *


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
    host, port = server_config.get_host(), server_config.get_port()
    fifo_dequeuer = RequestProcessor(TourneyRequestHandler.queue)

    try:
        # start up the fifo dequeuer
        fifo_dequeuer.start()

        # Create the server
        server = socketserver.TCPServer((host, port), TourneyRequestHandler)
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

