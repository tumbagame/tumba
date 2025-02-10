from queue import Queue

import time

class EventQueue:
    def __init__(self):
        self.funqueue = Queue()

    def add_event(self, function):
        self.funqueue.put(function)
        start_time = time.time()
        while not self.funqueue.empty():
            if (time.time() - start_time) > 5:
                return
    def run_event(self):
        if not self.funqueue.empty():
            self.funqueue.get_nowait()()

        
