#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
import zte

def connect():
	print "Connecting..."
	return

def disconnect():
	print "Disconnecting..."
	return

def ping(modem):
	zte.sendSMS(modem, "0882506400", "pong")
	return

def reboot():
	print "Rebooting..."
	return


def main():
	modem = zte.openModem('/dev/ttyUSB1', 5)
	if modem != -1:
		print zte.flushBuffer(modem)
		zte.setModemTextMode(modem)
		zte.sendSMS(modem, '0882506400', 'Pi is online. Waiting for commands.')
		while True:
			line = zte.readLineFromModem(modem)
			print line
			if line.startswith("+CMTI"):
				messageIndex = zte.getMessageIndex(line)
				messageBody = zte.readSMS(modem, messageIndex)
				zte.deleteSMS(modem, messageIndex)

				if messageBody.startswith("CMD"):
					command = messageBody.split(":")[1]
					if command.lower() == "connect":
						connect()
					elif command.lower() == "disconnect":
						disconnect()
					elif command.lower() == "ping":
						ping(serialPort)
					elif command.lower() == "reboot":
						reboot()
				else:
					print "Error. Invalid command format."


		zte.closeModem(modem)

	return


if __name__ == '__main__':
	main()

