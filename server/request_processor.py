from threading import Thread
import time
import queue
from datetime import datetime

import util.format as fmt
import tournament.main as tourney
from server.request_types import *
from tournament.state.tourney_snapshot import TourneySnapshot
from emailer import emailer
from util import paths
from util.funcs import print_tourney_trace


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

        print_tourney_trace("RequestProcessor started...")
        while self.process_requests:
            try:
                request = self.queue.get(block=False)
                if request.request_type == RequestType.SUBMIT:
                    print_tourney_trace("Processing submission by {}".format(request.submitter))
                    tourney.run_submission(request.submitter)

                elif request.request_type == RequestType.REPORT:
                    print_tourney_trace("Generating report for tournament submissions as of {}".format(request.time))
                    report_time = datetime.strptime(request.time, fmt.datetime_iso_string)
                    snapshot = TourneySnapshot(report_time=report_time)
                    snapshot.write_snapshot()
                    emailer.email_results(paths.get_snapshot_file_path(report_time), request.email)

                else:
                    pass

            except queue.Empty:
                print_tourney_trace("Queue empty. Nothing to pop")
                time.sleep(60)

        self.shutdown()

    def shutdown(self):
        """
        Shutdown hook for the RequestProcessor
        """
        print_tourney_trace("RequestProcessor closing with queue:" + str(self.queue.get_contents()))

    def stop(self):
        """
        Notify the RequestProcessor to stop processing new requests.
        """
        # TODO When processing takes a long tine RequestProcessor may not stop until well after this call is made

        self.process_requests = False
