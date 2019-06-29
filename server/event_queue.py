import queue
import threading
from collections import deque


class EventQueue(queue.Queue):
    """
    Extends queue.Queue to allow for more complex options than just push and pop.
    """

    def __init__(self):
        self.mut = threading.Lock()
        queue.Queue.__init__(self)

    def _put(self, item):
        """
        Default queue just pushes to the end of the queue.
        Check that the item doesn't already exist in queue. If it does remove it and add the new occurrence of item
        :param item: the item to add to the queue
        """

        with self.mut:
            ls = deque()

            while self.queue:
                i = self.queue.popleft()
                # if item in deque matches new item, remove the existing item
                if i == item:
                    pass
                else:
                    ls.append(i)

            ls.append(item)

            self.queue = ls

    def _get(self):
        """
        Pop the first item in the queue
        :return: the first item in the queue
        """
        with self.mut:
            return self.queue.popleft()

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
