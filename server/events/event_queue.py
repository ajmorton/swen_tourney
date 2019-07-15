import queue
import threading
from collections import deque
import tournament.config.paths as paths
import subprocess


class EventQueue(queue.Queue):
    """
    Extends queue.Queue to allow for more complex options than just push and pop.
    """

    def __init__(self):
        self.mut = threading.Lock()
        queue.Queue.__init__(self)

    def _put(self, new_event):
        """
        Add the new event to the end of the queue.
        If the new event is a 'submit' event, and the submitter has made a previous
        submission, then the previous submission can be removed provided there is
        no 'report' event in between the two.
        :param new_event: the event to add to the queue
        """

        with self.mut:
            ls = deque()
            report_found = False

            while self.queue:
                # pop events in reverse order
                event = self.queue.pop()

                if event['type'] == 'report':
                    report_found = True

                # if a previous 'submit' event with the same submitter is found with
                # no 'report' event between them then remove it
                if event == new_event and new_event['type'] == 'submit' and not report_found:
                    pass
                else:
                    ls.append(event)

            ls.reverse()
            ls.append(new_event)

            self.queue = ls

            if new_event['type'] == "submit":
                staged_dest = paths.STAGING_DIR + "/" + new_event['submitter']

                subprocess.run("rm -rf {}".format(staged_dest), shell=True)
                subprocess.run("cp -rf {} {}".format(new_event['dir'], staged_dest), shell=True)

    def _get(self):
        """
        Pop the first item in the queue
        :return: the first item in the queue
        """
        with self.mut:
            popped_event = self.queue.popleft()
            if popped_event['type'] == "submit":
                staged_dir = paths.STAGING_DIR + "/" + popped_event['submitter']
                tourney_dest = paths.TOURNEY_DIR + "/" + popped_event['submitter']
                subprocess.run("rm -rf {}".format(tourney_dest), shell=True)
                subprocess.run("cp -rf {} {}".format(staged_dir, tourney_dest), shell=True)
                subprocess.run("rm -rf {}".format(staged_dir), shell=True)

            return popped_event

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
