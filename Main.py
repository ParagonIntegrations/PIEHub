#! /usr/bin/env python3

import multiprocessing
import queue
import datetime
import time
import sqlite3
import serial
import json
import os


# Class for writing to Database
class DBServ(multiprocessing.Process):

    def __init__(self, inputqueue, outputqueue):
        multiprocessing.Process.__init__(self)

        # Use correct communication queues
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue

        # Initialize variables
        self.databaselist = []
        self.lastsleeptime = 0

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "PIEHub.db")

    def write_to_database(self):
        print(self.databaselist)
        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                conn.executemany('INSERT INTO EnergyLog(DateTime, V, I)'
                                 ' VALUES (:DateTime, :V, :I)',
                                 self.databaselist)
            print('Data written to database - DBServ')
        except sqlite3.Error as e:
            # print("sqlite3 error - DBServ")
            print("An error occurred:", e.args[0])
        self.databaselist = []

    def run(self):

        while True:

            # Get updated variables from queue
            try:
                while True:
                    updated_variables = self.inputqueue.get_nowait()
                    self.databaselist.append(updated_variables)
                    #print("Data received - WriteTODatabase")
            except queue.Empty:
                pass

            # Check length of list to write
            if len(self.databaselist) >= 50:
                self.write_to_database()

            time.sleep(1)


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
        ser = serial.Serial(port="/dev/ttyAMA0",baudrate=500000,timeout=10)
        ser.close()
        ser.open()

        #Initialize default dictionary
        defaults = {
            'DateTime': 'Default Timestamp',
            'V': 0,
            'I': 0
        }

        safedict = {}

        while True:

            self.data = ser.readline().strip()
            decodeddata = self.data.decode()
            print(decodeddata)
            if decodeddata != "":
                try:
                    decodeddict = json.loads(decodeddata)
                    decodeddict['DateTime'] = datetime.datetime.now().isoformat(timespec='milliseconds')
                    #print('Json')
                    #print("")
                    #print (json.dumps(decodeddict, indent=1, sort_keys=True))
                    for k in defaults:
                        safedict[k] = decodeddict.get(k, defaults[k])
                    self.outputqueue.put(safedict)
                except Exception:
                    print("Exception ignored in decoding json data - SerialComm")


# Main Manager class
class HubManager(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

        # Initialize variables
        self.Processdata = {}

    def run(self):

        # Start subprocesses
        # Start Serial Reader
        self.Processdata['SerialComm'] = {}
        self.Processdata['SerialComm']['inputqueue'] = multiprocessing.Queue()
        self.Processdata['SerialComm']['outputqueue'] = multiprocessing.Queue()
        SerialComm(self.Processdata['SerialComm']['inputqueue'],self.Processdata['SerialComm']['outputqueue']).start()
        print('Serial Comm Started - PIEHub')

        # Start the Database manager
        self.Processdata['DBServ'] = {}
        self.Processdata['DBServ']['inputqueue'] = multiprocessing.Queue()
        self.Processdata['DBServ']['outputqueue'] = multiprocessing.Queue()
        DBServ(self.Processdata['DBServ']['inputqueue'], self.Processdata['DBServ']['outputqueue']).start()
        print('DB Server started - PIEHub')

        # Main Loop
        while True:

            # Check for new data from PIEmon
            try:
                while True:
                    self.serialdata = self.Processdata['SerialComm']['outputqueue'].get_nowait()
                    # Send data to Database
                    self.Processdata['DBServ']['inputqueue'].put(self.serialdata)
                    #print("Data sent to DB - Hub Manager")
            except queue.Empty:
                pass

            # Send updated information to PIEmon every 60 mins

            time.sleep(1)




if __name__ == "__main__":
    print("Waiting 30 seconds before starting")
    time.sleep(30)
    hubman = HubManager()
    hubman.start()
    hubman.join()


"""
Things to do:



"""