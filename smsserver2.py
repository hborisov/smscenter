#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii

def connect():
	print "Connecting..."
#	global wvdial
	stout = open("stdout.log", 'wb')
	sterr = open("stderr.log", 'wb')
	wvdial = subprocess.Popen(["wvdial", "3gconnect"], stdout=stout, stderr=sterr)		
#	time.sleep(5)	
#	wvdial.terminate()
#	return wvdial
	return

def disconnect():
	print "Disconnecting..."
#	print wvdial.terminate()
	return

def ping(serialPort):
	print "PONG..."
	print serialPort.isOpen()
	serialPort.write('AT+CMGS="%s"\r\n' %"+359882506400")
	serialPort.write("PONG")
	serialPort.write(ascii.ctrl('z'))
	print "PONG status: " + readATCommandResult(serialPort)
	return

def reboot():
	print "Rebooting..."
	return

def readCommand(serialPort):
	while True:
		currentLine = serialPort.readline()
		if currentLine == "OK\r\n" or currentLine == "ERROR\r\n":
			return currentLine
			break
		elif currentLine.startswith("CMD:"):
			command = currentLine.split(":")[1]
			return command.strip()
	return "ERROR"

def readATCommandResult(serialPort):
	#while True:
	#	currentLine = serialPort.readline()
	#	if currentLine == "OK\r\n" or currentLine.startswith("ERROR"):
	#		return currentLine
	lines = serialPort.readlines()
	lastelement = len(lines) - 1
	return lines[lastelement]


def handleNewSMS(serialPort, indication):
	newSMSIndicationParts = indication.split(":")
	print newSMSIndicationParts[1]
	messageIndex = newSMSIndicationParts[1].split(",")[1]
	print messageIndex
	serialPort.write("AT+CMGR=" + messageIndex + "\r")
	command = readCommand(ser)
	print "Command is: " + command
	deleteSMS(serialPort, messageIndex)

	if command.lower() == "connect":
		connect()
	elif command.lower() == "disconnect":
		disconnect()
	elif command.lower() == "ping":
		ping(serialPort)
	elif command.lower() == "reboot":
		reboot()
	return

def deleteSMS(serialPort, SMSIndex):
	print "Deleteing message: " + SMSIndex
	serialPort.write("AT+CMGD=" + SMSIndex + "\r")
	deleteCommandStatus = readATCommandResult(serialPort)
	print "Delete: " + deleteCommandStatus
	return deleteCommandStatus

DEVNULL = open(os.devnull, 'wb')

ser = serial.Serial('/dev/ttyUSB1', 460800, timeout=5)
print ser.name

print ser.readlines()

ser.write("AT+CMGF=1\r")
print ser.readline()
print ser.readline()

ser.write('AT+CMGS="0882506400"\r\n')
ser.write('Pi is online. Waiting for commands.')
ser.write(ascii.ctrl('z'))
print ser.readline()
print ser.readline()
print ser.readline()
print ser.readline()

while True:
	line = ser.readline()
	print line
	if line.startswith("+CMTI"):
		handleNewSMS(ser, line)
#		break
		

print "exiting..."
if ser.isOpen == True:
	ser.close()
DEVNULL.close()
