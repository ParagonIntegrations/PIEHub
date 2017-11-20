#! /usr/bin/env python3

import multiprocessing
import queue
import datetime
import time
import sqlite3
import serial
import json


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
        conn = sqlite3.connect('PIEHub.db')
        try:
            with conn:
                conn.executemany('INSERT INTO EnergyLog(DateTime, ID, Frequency, PLL, V1, I1,'
                                 ' PowerFactor1, PImport1, PExport1, UnitsUsed1, Units1)'
                                 ' VALUES (:DateTime, :ID, :Frequency, :PLL, :V1, :I1,'
                                 ' :PowerFactor1, :PImport1, :PExport1, :UnitsUsed1, :Units1)',
                                 self.databaselist)
            print('Data written to database - WriteToDatabase')
        except sqlite3.Error:
            print("sqlite3 error - WriteToDatabase")
        self.databaselist = []

    def run(self):

        while True:

            # Get updated variables from queue
            try:
                while True:
                    updated_variables = self.inputqueue.get_nowait()
                    self.databaselist.append(updated_variables)
                    print("Data received - WriteTODatabase")
            except queue.Empty:
                pass

            # Check length of list to write
            if len(self.databaselist) > 6:
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
        ser = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=10)
        ser.close()
        ser.open()


        while True:

            self.data = ser.readline().strip()
            #print(self.data)
            decodeddata = self.data.decode()

            if decodeddata != "":
                try:
                    decodeddict = json.loads(decodeddata)
                    decodeddict['DateTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    #print('Json')
                    #print("")
                    #print (json.dumps(decodeddict, indent=1, sort_keys=True))
                    self.outputqueue.put(decodeddict)
                except Exception:
                    print("Exception ignored in decoding json data - SerialComm")

            # Check inputqueue for new information
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
        self.serialdata = {
            'ID': 0,
            'Units1': 0,
            'UnitsUsed1': 0
        }
        self.EnergyData = {}


    def run(self):

        # Start subprocesses
        #Start Serial Reader
        self.Processdata['SerialComm'] = {}
        self.Processdata['SerialComm']['inputqueue'] = multiprocessing.Queue()
        self.Processdata['SerialComm']['outputqueue'] = multiprocessing.Queue()
        SerialComm(self.Processdata['SerialComm']['inputqueue'],self.Processdata['SerialComm']['outputqueue']).start()
        print('Serial Comm Started - PIEHub')

        # Start the Database manager
        self.Processdata['DBServ'] = {}
        self.Processdata['DBServ']['inputqueue'] = multiprocessing.Queue()
        self.Processdata['DBServ']['outputqueue'] = multiprocessing.Queue()
        WriteToDatabase(self.Processdata['DBServ']['inputqueue'], self.Processdata['DBServ']['outputqueue']).start()
        print('DB Server started - PIEHub')

        # Main Loop
        while True:

            # Check for new data from PIEmon
            try:
                while True:
                    self.serialdata = self.Processdata['SerialComm']['outputqueue'].get_nowait()
            except queue.Empty:
                pass

            # Update Energy variables
            UnitID = self.serialdata['ID']
            print(UnitID)

            if UnitID not in self.EnergyData.keys():
                self.EnergyData[UnitID] = {
                        'Units1': 0,
                        'UnitsUsed1': 0
                }
            else:
                self.EnergyData[UnitID]['UnitsUsed1'] = self.serialdata['UnitsUsed1']
                self.EnergyData[UnitID]['Units1'] -= self.serialdata['Units1']
                # Check if Units match

            # Send data to Database
            self.Processdata['DBServ']['inputqueue'].put(self.serialdata)
            print("Data sent to DB - Hub Manager")

            # Send updated information to PIEmon every 60 mins



            time.sleep(1)

if __name__ == "__main__":
    hubman = HubManager()
    hubman.start()
    hubman.join()


"""
Things to do:



"""