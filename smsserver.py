#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
from zte import zte

pid = -1
child = None
tunnelchild = None

def checkConnection():
	DEVNULL = open(os.devnull, 'wb')
	print "Checking connection status..."
        try:
            result = subprocess.check_call(["ping", "-c", "5", "www.abv.bg"],stdout=DEVNULL, stderr=DEVNULL)
        except subprocess.CalledProcessError, ex: # error code <> 0 
            result = ex.returncode

        DEVNULL.close()
	print "Connection status: " + str(result)
	return result

def connect():
	print "Connecting..."
	DEVNULL = open(os.devnull, 'wb')

	connectionIsOpen = checkConnection()

	if connectionIsOpen != 0:
		global child
		try:
			child = subprocess.Popen(["wvdial", "3gconnect"], stdout=DEVNULL, stderr=DEVNULL)
		except subprocess.CalledProcessError, ex: # error code <> 0 
			print "Error starting wvdial."
	    		print ex.returncode
	    		return -1
	else:
		print "Connection is already opened."


def disconnect():
	print "Disconnecting..."
	global child
	print "closing: " + str(child.pid)
	child.terminate()	
	child.wait()	

def ping(modem):
	print "pong..."
	zte.sendSMS(modem, "0882506400", "pong")

def reboot():
	print "Rebooting..."
	subprocess.call(["sudo", "/sbin/reboot"])

def status(modem):
	print "Sending status information..."

	print "Getting disk usage..."
	diskUsage = subprocess.check_output(["/bin/df", "-h", "/dev/root"])
	diskUsage = diskUsage.split("\n")[1]
	print diskUsage

	print "Getting connection status"
	connectionStatus = checkConnection()
	if connectionStatus == 0:
		connectionStatus = "CONNECTED"
	else:
		connectionStatus = "DISCONNECTED"
	statusText = "Pi is %s, t is %s, prsr s %s\rdisk usage: %s" % (connectionStatus, "20.0", "95", diskUsage)
	print statusText
	print "Sending status..."
	print zte.sendSMS(modem, "0882506400", statusText)

def openTunnel(remotePort, localPort, toAddress):
	portSpecification = "%s:localhost:%s" % (remotePort, localPort)
	print "Opening tunnel to: " + portSpecification

	DEVNULL = open(os.devnull, 'wb')
	try:
		global tunnelchild
		tunnelchild = subprocess.Popen(["ssh", "-nNT", "-R", portSpecification, toAddress], stdout=DEVNULL, stderr=DEVNULL)
	except subprocess.CalledProcessError, ex:
		print "Error opening tunnel"
		return ex.returncode

	print "Tunnel opened"

def closeTunnel():
	print "Closing tunnel"
	global tunnelchild
	tunnelchild.terminate()
	tunnelchild.wait()
	print "Tunnel closed"
	

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
					elif command.lower() == "status":
						status(modem)
					elif command.lower().startswith("tunnel"):
						tunnelCommandParts = command.split(",")
						remotePort = tunnelCommandParts[1]
						localPort = tunnelCommandParts[2]
						address = tunnelCommandParts[3]
						openTunnel(remotePort, localPort, address)
					elif  command.lower() == "closetunnel":
						closeTunnel()
					else:
						print "Unknown command."
				else:
					print "Error. Invalid command format."



		zte.closeModem(modem)

	return


if __name__ == '__main__':
	main()
