#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
import sys

def sendsms(phoneNumber, text):
	ser = serial.Serial('/dev/ttyUSB1', 460800, timeout=1)
	print ser.name

	ser.write("AT\r\n")
	line = ser.readline(size=None, eol='\r\n')
#	line = ser.readline()
	print line

	ser.write("AT+CMGF=1\r\n")
	line = ser.readline(size=None, eol='\r\n')
#	line = ser.readline()
	print line
#	print ser.readline()

	ser.write('AT+CMGS="%s"\r\n' %phoneNumber)
	ser.write(text)
	ser.write(ascii.ctrl('z'))
	time.sleep(3)
	print ser.readline()
	print ser.readline()
	print ser.readlines()

	ser.close()
	return

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Wrong number of arguments"
		print "Usage: sendsms.py <phone number> <message text>"
		sys.exit(-1)

	phoneNumber = sys.argv[1]
	smsText = sys.argv[2]
	sendsms(phoneNumber, smsText)
