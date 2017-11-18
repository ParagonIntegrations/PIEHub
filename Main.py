#! /usr/bin/env python3

import multiprocessing
import queue
import time
import sqlite3
import serial


# Class for writing to Database
class WriteToDatabase(multiprocessing.Process):

    def __init__(self, inputqueue, outputqueue):
        multiprocessing.Process.__init__(self)

        # Use correct communication queues
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue

        # Initialize variables
        self.databaselist = []
        self.lastsleeptime = 0

    def write_to_database(self):
        conn = sqlite3.connect('Log.db')
        try:
            with conn:
                conn.executemany('INSERT INTO PIDOutput(DateTime, ProcessName, Temperature, Duty, Setpoint,'
                                 'SafetyTemp, SafetyTrigger, Status) VALUES (:DateTime, :ProcessName,'
                                 ':Temperature, :Duty, :Setpoint, :SafetyTemp, :SafetyTrigger, :Status)',
                                 self.databaselist)
        except sqlite3.Error:
            pass
        self.databaselist = []

    def run(self):

        while True:

            # Get updated variables from queue
            try:
                while True:
                    updated_variables = self.inputqueue.get_nowait()
                    self.databaselist.append(updated_variables)
            except queue.Empty:
                pass

            # Check length of list to write
            if len(self.databaselist) > 50:
                self.write_to_database()

            time.sleep(2)


# Class for reading and writing to the serial port
class SerialComm(multiprocessing.Process):

    def __init__(self, inputqueue, outputqueue):
        multiprocessing.Process.__init__(self)

        # Use correct communication queues
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue

        # Initialize variables
        self.data = "1"

    def run(self):
        # Initialize serial connection
        ser = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=2)
        ser.close()
        ser.open()


        while True:

            self.data = ser.readline()
            print(self.data)

            # Get information from Queue
            try:
                while True:
                    updated_variables = self.inputqueue.get_nowait()
                    ser.write(updated_variables)
            except queue.Empty:
                pass



# Main Manager class
class HubManager(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

        # Initialize variables
        self.Processdata = {}


    def run(self):

        # Start subprocesses
        #Start Serial Reader
        self.Processdata['SerialComm'] = {}
        self.Processdata['SerialComm']['inputqueue'] = multiprocessing.Queue
        self.Processdata['SerialComm']['outputqueue'] = multiprocessing.Queue
        SerialComm(self.Processdata['SerialComm']['inputqueue'],self.Processdata['SerialComm']['outputqueue']).start()
        print('Serial Comm Started')
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