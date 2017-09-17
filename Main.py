#! /usr/bin/env python3

import multiprocessing
import time
import sqlite3




class HubManager(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)


    def run(self):

        # Start subprocesses

        # Main Loop
        while True:

            # Check for new data from PIEmon

            # Update Energy variables

            # Send data to Database

            # Send updated information to PIEmon every 60 mins



            time.sleep(1)

if __name__ == "__main__":
    hubman = HubManager()
    hubman.start()
    hubman.join()


"""
Things to do:



"""