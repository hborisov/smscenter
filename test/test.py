#!/usr/bin/python
import serial
import time
import subprocess
import os
import sys
from curses import ascii

def rline(modem, eol):
	eollength = len(eol)
	lne = bytearray()
	print "rline"
	while True:
		char = modem.read(1)
#		print ord(char)
		if char:
			lne += char
			#print lne[-eollength:]
			if lne[-eollength:] == eol:
				break
		else:
			break
	return bytes(lne[:-2])

try:
	ser = serial.Serial('/dev/gsmmodem', 460800, timeout=2)
	print ser.name
except Exception, e:
	print e
	sys.exit(-1)

ser.write("AT\r")
#line = ser.readline(size=None, EOL='\r\n')
#print line
#line = ser.readline()
#print line
print rline(ser, '\r\n')
print rline(ser, '\r\n')

ser.write("AT+CMGF=1\r")
print rline(ser, '\r\n')
print rline(ser, '\r\n')

ser.write('AT+CMGS="0882506400"\r\n')
ser.write('text')
ser.write(ascii.ctrl('z'))
print rline(ser, '\r\n')
print rline(ser, '\r\n')
print rline(ser, '\r\n')
print rline(ser, '\r\n')
print rline(ser, '\r\n')
