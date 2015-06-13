#!/usr/bin/python
import serial
import time
import subprocess
import os

DEVNULL = open(os.devnull, 'wb')

ser = serial.Serial('/dev/gsmmodem', 460800, timeout=1)
print ser.name

ser.write("AT\r")
line = ser.readline()
print line
line = ser.readline()
print line

ser.write("AT+CMGF=1\r")
line = ser.readline()
print line
line = ser.readline()
print line

ser.write("AT+CMGL=\"REC UNREAD\"\r")
while True:
	line = ser.readline()
	print line
	if line.startswith("+CMGL"):
		continue
	else:
		print line
		if line == "Connect\r\n":
			print "executing"
			subprocess.Popen(["sudo", "wvdial", "3gconnect", "&"], stdout=DEVNULL, stderr=DEVNULL)
			print "connection started"
			exit(0)
	if line == "OK\r\n" or line == "ERROR\r\n":
		break


ser.close()
DEVNULL.close()
