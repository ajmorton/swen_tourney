import queue
import threading
from collections import deque
import tournament.config.paths as paths
import subprocess

from server.request_types import *


class RequestQueue(queue.Queue):
    """
    Extends queue.Queue to allow for more complex options than just push and pop.
    """

    def __init__(self):
        self.mut = threading.Lock()
        queue.Queue.__init__(self)

    def _put(self, new_request):
        """
        Add the new request to the end of the queue.
        If the new request is a 'submit' request, and the submitter has made a previous
        submission, then the previous submission can be removed provided there is
        no 'report' request in between the two.
        :param new_request: the request to add to the queue
        """

        with self.mut:
            ls = deque()
            report_found = False

            while self.queue:
                # pop requests in reverse order
                queued_request = self.queue.pop()

                if queued_request.request_type == RequestType.REPORT:
                    report_found = True

                # if a previous 'submit' request with the same submitter is found with
                # no 'report' request between them then remove it
                if queued_request == new_request \
                        and new_request.request_type == RequestType.SUBMIT and not report_found:
                    pass
                else:
                    ls.append(queued_request)

            ls.reverse()
            ls.append(new_request)

            self.queue = ls

            if new_request.request_type == RequestType.SUBMIT:
                pre_validation_dir = paths.PRE_VALIDATION_DIR + "/" + new_request.submitter
                staged_dest = paths.STAGING_DIR + "/" + new_request.submitter

                subprocess.run("rm -rf {}".format(staged_dest), shell=True)
                subprocess.run("cp -rf {} {}".format(pre_validation_dir, staged_dest), shell=True)

    def _get(self):
        """
        Pop the first item in the queue
        :return: the first item in the queue
        """
        with self.mut:
            popped_request = self.queue.popleft()
            if popped_request.request_type == RequestType.SUBMIT:
                staged_dir = paths.STAGING_DIR + "/" + popped_request.submitter
                tourney_dest = paths.TOURNEY_DIR + "/" + popped_request.submitter
                subprocess.run("rm -rf {}".format(tourney_dest), shell=True)
                subprocess.run("cp -rf {} {}".format(staged_dir, tourney_dest), shell=True)
                subprocess.run("rm -rf {}".format(staged_dir), shell=True)

            return popped_request

    def get_contents(self):
        """
        Fetch the contents of the queue as a list
        :return: the contents of the queue as a list
        """
        ls = list()

        with self.mut:
            while self.queue:
                ls.append(self.queue.popleft())

            for x in ls:
                self.queue.append(x)

        return ls
