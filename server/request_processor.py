from threading import Thread
import time
import queue
from datetime import datetime
import tournament.main as tourney
from server.request_types import *
import tournament.state.reporting as reporting
from tournament.config import config


class RequestProcessor(Thread):
    """
    A thread that pops the first item off of the RequestQueue and processes it.
    """

    # Thread runs forever unless process_requests is set to false
    process_requests = True

    def __init__(self, request_queue):
        self.queue = request_queue
        Thread.__init__(self)

    def run(self):
        """
        Pop requests from the RequestQueue and process them forever, or until process_requests flag is set to False
        """

        print("RequestProcessor started...")
        while self.process_requests:
            try:
                request = self.queue.get(block=False)
                if request.request_type == RequestType.SUBMIT:
                    print("Processing submission by {}".format(request.submitter))
                    tourney.run_submission(request.submitter)

                elif request.request_type == RequestType.REPORT:
                    print("Generating report for tournament submissions as of {}".format(request.time))
                    reporting.generate_report(datetime.strptime(request.time, config.date_iso_format), request.email)

                else:
                    pass
            except queue.Empty:
                print("Nothing to pop from queue")
            time.sleep(8)

        self.shutdown()

    def shutdown(self):
        """
        Shutdown hook for the RequestProcessor
        """
        print("RequestProcessor closing with queue:")
        ls = self.queue.get_contents()
        for request in ls:
            print(request)

    def stop(self):
        """
        Notify the RequestProcessor to stop processing new requests.
        """
        # TODO When processing takes a long tine RequestProcessor may not stop until well after this call is made

        self.process_requests = False
