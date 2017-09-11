#! /usr/bin/env python3

import multiprocessing
import time


class HubManager(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):

        # Main Loop
        while True:

            time.sleep(1)

if __name__ == "__main__":
    hubman = HubManager()
    hubman.start()
    hubman.join()
