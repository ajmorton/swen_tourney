import json
import queue
import os
import threading
from collections import deque
from util import paths
import tournament.main as tourney
import subprocess

from server.request_types import *
from util.types import Submitter


class RequestQueue(queue.Queue):
    """
    Extends queue.Queue to allow for more complex options than just push and pop.
    """

    def __init__(self):
        queue.Queue.__init__(self)
        self.mut = threading.Lock()
        self.queue = deque()
        self.version_numbers = ["", "_v2", "_v3", "_v4", "_v5"]

        self.restore_queue()

    def restore_queue(self):
        """
        Restore the queue based on the contents of the staged/ directory
        """
        ls = subprocess.run(
            "ls -rt {}".format(paths.STAGING_DIR),
            shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )

        for file in ls.stdout.split("\n"):
            if file.startswith("report_request"):
                report_file = json.load(open(paths.STAGING_DIR + "/" + file, 'r'))
                self.queue.append(request_from_json(report_file))
            elif file != "":
                if file[-3:] in self.version_numbers:
                    file = file[:-3]
                self.queue.append(SubmissionRequest(file))

    def _put(self, request):

        with self.mut:
            if request.request_type == RequestType.SUBMIT:
                self.put_submission(request)
            elif request.request_type == RequestType.REPORT:
                self.put_report(request)
            else:
                print("Error: Unexpected {} request being added to request_queue".format(request.request_type))

    def put_submission(self, submission_request: SubmissionRequest):
        """
        Add the new request to the end of the queue.
        If the submitter has made a previous submission, then the previous submission can be removed provided there is
        no 'report' request in between the two.
        :param submission_request: the submission request to add to the queue
        """

        ls = deque()
        report_found = False

        while self.queue:
            # pop requests in reverse order
            queued_request = self.queue.pop()

            if queued_request.request_type == RequestType.REPORT:
                report_found = True

            # if a previous 'submit' request with the same submitter is found with
            # no 'report' request between them then remove it
            if queued_request == submission_request \
                    and submission_request.request_type == RequestType.SUBMIT and not report_found:
                # remove the previous submission
                subprocess.run(
                    "rm -rf {}".format(tourney.get_most_recent_staged_submission(submission_request.submitter)),
                    shell=True
                )
            else:
                ls.append(queued_request)

        ls.reverse()
        ls.append(submission_request)

        while ls:
            self.queue.append(ls.popleft())

        # copy the submission into the staging dir
        pre_validation_dir = paths.get_pre_validation_dir(submission_request.submitter)

        # if a submission is already staged for the user, add the new one as submitter_v2, _v3 etc
        for vers in self.version_numbers:
            staged_dest = paths.get_staging_dir(submission_request.submitter) + vers

            if not os.path.isdir(staged_dest):
                subprocess.run("mv {} {}".format(pre_validation_dir, staged_dest), shell=True)
                break

    def put_report(self, report_request: ReportRequest):
        """
        Add a report request to the queue
        :param report_request: the request to add
        """
        self.queue.append(report_request)

        # create a report file in the staging dir
        report_request_file = paths.get_staged_report_request_filename(report_request.time)
        with open(report_request_file, 'w') as outfile:
            json.dump(report_request, outfile, indent=4)

    def _get(self):
        """
        Pop the first item in the queue
        :return: the first item in the queue
        """
        with self.mut:
            request = self.queue.popleft()
            if request.request_type == RequestType.SUBMIT:
                staged_dir = paths.get_staging_dir(request.submitter)
                tourney_dest = paths.get_tourney_dir(request.submitter)

                tourney.write_metadata(request.submitter)

                subprocess.run("rm -rf {}".format(tourney_dest), shell=True)
                subprocess.run("mv {} {}".format(staged_dir, tourney_dest), shell=True)
                self.update_vers(request.submitter)

            elif request.request_type == RequestType.REPORT:
                report_request_file = paths.get_staged_report_request_filename(request.time)
                subprocess.run("rm -f {}".format(report_request_file), shell=True)

            return request

    def update_vers(self, submitter: Submitter):
        """
        In the staged directory change submissions from submitter_v2 to submitter, submitter_v3 to submitter_v2 etc
        :param submitter: the submitter whose submissions should be updated
        """
        for i in range(1, len(self.version_numbers)):
            old_dir = paths.get_staging_dir(submitter) + self.version_numbers[i]
            if os.path.isdir(old_dir):
                new_dir = paths.get_staging_dir(submitter) + self.version_numbers[i - 1]
                # Use cp -p to preserve timestamp information, used in restore_queue()
                subprocess.run("cp -rp {} {}".format(old_dir, new_dir), shell=True)
                subprocess.run("rm -rf {}".format(old_dir), shell=True)

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
