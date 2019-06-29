from threading import Thread
import time
import queue


class EventProcessor(Thread):
    """
    A thread that pops the first item off of the EventQueue and processes it.
    """

    # Thread runs forever unless process_events is set to false
    process_events = True

    def __init__(self, request_queue):
        self.queue = request_queue
        Thread.__init__(self)

    def run(self):
        """
        Pop events from the EventQueue and process them forever, or until process_events flag is set to False
        :return:
        """

        print("EventProcessor started...")
        while self.process_events:
            try:
                event = self.queue.get(block=False)
                event_type = event['type']
                if event_type == 'submit':
                    print("Submission from {}".format(event['submitter_name']))
                elif event_type == 'report':
                    print("Making report, sending to {}".format(event['requester_email']))
            except queue.Empty:
                print("Nothing to pop from queue")
            time.sleep(20)

        self.shutdown()

    def shutdown(self):
        """
        Shutdown hook for the EventProcessor
        """
        print("EventProcessor closing with queue: {}".format(self.queue.get_contents()))

    def stop(self):
        """
        Notify the EventProcessor to stop processing new events.
        """
        # TODO When processing takes a long tine EventProcessor may not stop until well after this call is made

        self.process_events = False
