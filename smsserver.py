#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
import zte

pid = -1

def connect():
	print "Connecting..."
	connectionStatus = subprocess.check_output("/home/pi/sms/check_connection.py")
	print "Connection status is: " + connectionStatus
	print type(connectionStatus)
	if connectionStatus != "0":
		global pid
		pid = subprocess.check_output("/home/pi/sms/open_connection.py")
		print "PID is: " + pid
	return

def disconnect():
	print "Disconnecting..."
	global pid
	print "closing: " + str(pid)
	subprocess.check_output(["/home/pi/sms/open_connection.py", str(pid)])
	
	connectionStatus = subprocess.check_output("/home/pi/sms/check_connection.py")
	print "Connection status is: " + connectionStatus
	
	return

def ping(modem):
	print "pong..."
	zte.sendSMS(modem, "0882506400", "pong")
	return

def reboot():
	print "Rebooting..."
	subprocess.call("sudo reboot")
	return


def main():
	modem = zte.openModem('/dev/ttyUSB1', 5)
	if modem != -1:
		print zte.flushBuffer(modem)
		zte.setModemTextMode(modem)
#		zte.sendSMS(modem, '0882506400', 'Pi is online. Waiting for commands.')
		while True:
			print modem.isOpen()
			if not modem.isOpen():
				modem = zte.openModem('/dev/ttyUSB1', 5)
				print zte.flushBuffer(modem)
				zte.setModemTextMode(modem)

			line = zte.readLineFromModem(modem)
			print line

			if line.startswith("+CMTI"):
				messageIndex = zte.getMessageIndex(line)
				print messageIndex
				messageBody = zte.readSMS(modem, messageIndex)
				print messageBody
				zte.deleteSMS(modem, messageIndex)

				if messageBody.startswith("CMD"):
					command = messageBody.split(":")[1].strip()
					print "Command is: " + command
					
					if command.lower() == "connect":
						connect()
						print "Connected"
						zte.closeModem(modem)
					elif command.lower() == "disconnect":
						disconnect()
						print "Disconnected"
						zte.closeModem(modem)
					elif command.lower() == "ping":
						ping(modem)
					elif command.lower() == "reboot":
						reboot()
				else:
					print "Error. Invalid command format."



		zte.closeModem(modem)

	return


if __name__ == '__main__':
	main()

