#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
import zte

def connect():
	print "Connecting..."
	connectionStatus = subprocess.check_output("/home/pi/check_connection.py")
	print "Connection status is: " + connectionStatus
	return

def disconnect():
	print "Disconnecting..."
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
					elif command.lower() == "disconnect":
						disconnect()
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

