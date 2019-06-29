import socketserver
import json
from events.event_processor import EventProcessor
from events.event_queue import EventQueue

from config import server_config


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
        data = self.request.recv(1024).decode()
        event = json.loads(data)

        print('Event received: "{}"'.format(event))

        event_type = event['type']

        if event_type == "shutdown":
            self.request.sendall("SHUTTING_DOWN_SERVER".encode())
            self.server._BaseServer__shutdown_request = True
        elif event_type in {"submit", "report"}:
            self.queue.put(event)
            return_string = "\n".join([json.dumps(x) for x in list(self.queue.queue)])
            self.request.sendall(return_string.encode())
        else:
            print("Event type '{}' is not currently handled".format(event_type))


def event_to_str(event):
    if event['type'] == 'submit':
        return "Submit: {}".format(event['submitter_name'])
    elif event['type'] == 'report':
        return "Report to: {}".format(event['reporter_email'])
    else:
        return "Event {} not yet handled".format(event['type'])


def start_server():
    """
    Create the EventProcessor and SocketServer threads
    """
    host, port = server_config.get_host(), server_config.get_port()
    try:
        # start up the  fifo dequeuer
        fifo_dequeuer = EventProcessor(TourneyRequestHandler.queue)
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


if __name__ == "__main__":
    start_server()