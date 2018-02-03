#!/bin/bash
cd /
cd home/pi/PIEHub
sudo python3 Main.py
cd /


screen -S PIEHub -d -m sudo python3 /home/pi/PIEHub/Main.py