#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii

DEVNULL = open(os.devnull, 'wb')

ser = serial.Serial('/dev/ttyUSB1', 460800, timeout=1)
print ser.name

ser.write("AT\r\n")
line = ser.readline()
print line
line = ser.readline()
print line

ser.write("AT+CMGF=0\r\n")
line = ser.readline()
print line
line = ser.readline()
print line
print ser.readline()

#ser.write("AT+ZMSGL=1,2")
#print ser.readline()
#print ser.readline()
#print ser.readline()

ser.write('AT+CMGS=21\r')# %"359882506400")
ser.write("07915389080003F111000C915389280546000004FF0774657374696E67")
ser.write(ascii.ctrl('z'))
time.sleep(3)
print ser.readline()
print ser.readline()
print ser.readlines()

ser.close()
DEVNULL.close()
