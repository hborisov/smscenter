#!/usr/bin/python
import serial
import time
import subprocess
import os
from curses import ascii
from zte import zte
import logging
import logging.config

pid = -1
child = None
tunnelchild = None

logging.config.fileConfig('/home/pi/sms/logging_config.ini')
logger = logging.getLogger('smsserver')

def checkConnection():
	DEVNULL = open(os.devnull, 'wb')
	logger.info("Checking connection status...")
        try:
            result = subprocess.check_call(["ping", "-c", "5", "www.abv.bg"],stdout=DEVNULL, stderr=DEVNULL)
        except subprocess.CalledProcessError, ex: # error code <> 0 
            result = ex.returncode

        DEVNULL.close()
	logger.info("Connection status: " + str(result))
	return result

def connect():
	logger.info("Connecting...")
	DEVNULL = open(os.devnull, 'wb')

	connectionIsOpen = checkConnection()

	if connectionIsOpen != 0:
		global child
		try:
			child = subprocess.Popen(["wvdial", "3gconnect"], stdout=DEVNULL, stderr=DEVNULL)
		except subprocess.CalledProcessError, ex: # error code <> 0 
			logger.info("Error starting wvdial.")
	    		logger.info(ex.returncode)
	    		return -1
	else:
		logger.info("Connection is already opened.")


def disconnect():
	logger.info("Disconnecting...")
	global child
	logger.info("closing: " + str(child.pid))
	child.terminate()	
	child.wait()	

def ping(modem):
	logger.info("Pong...")
	zte.sendSMS(modem, "0882506400", "pong")

def reboot():
	logger.info("Rebooting...")
	subprocess.call(["sudo", "/sbin/reboot"])

def status(modem):
	logger.info("Sending status information...")

	logger.info("Getting disk usage...")
	diskUsage = subprocess.check_output(["/bin/df", "-h", "/dev/root"])
	diskUsage = diskUsage.split("\n")[1]
	logger.info(diskUsage)

	logger.info("Getting connection status")
	connectionStatus = checkConnection()
	if connectionStatus == 0:
		connectionStatus = "CONNECTED"
	else:
		connectionStatus = "DISCONNECTED"
	statusText = "Pi is %s, t is %s, prsr s %s\rdisk usage: %s" % (connectionStatus, "20.0", "95", diskUsage)
	logger.info(statusText)
	logger.info("Sending status...")
	logger.info(zte.sendSMS(modem, "0882506400", statusText))

def openTunnel(remotePort, localPort, toAddress):
	portSpecification = "%s:localhost:%s" % (remotePort, localPort)
	logger.info("Opening tunnel to: " + portSpecification)

	DEVNULL = open(os.devnull, 'wb')
	try:
		global tunnelchild
		tunnelchild = subprocess.Popen(["ssh", "-nNT", "-R", portSpecification, toAddress], stdout=DEVNULL, stderr=DEVNULL)
	except subprocess.CalledProcessError, ex:
		logger.info("Error opening tunnel")
		return ex.returncode

	logger.info("Tunnel opened")

def closeTunnel():
	logger.info("Closing tunnel")
	global tunnelchild
	tunnelchild.terminate()
	tunnelchild.wait()
	logger.info("Tunnel closed")
	

def main():
	modem = zte.openModem('/dev/ttyUSB1', 5)
	if modem != -1:
		logger.info(zte.flushBuffer(modem))
		zte.setModemTextMode(modem)
		zte.sendSMS(modem, '0882506400', 'Pi is online. Waiting for commands.')
		while True:
			logger.debug("Modem is open? %s" % modem.isOpen())
			if not modem.isOpen():
				modem = zte.openModem('/dev/ttyUSB1', 5)
				logger.info(zte.flushBuffer(modem))
				zte.setModemTextMode(modem)

			line = zte.readLineFromModem(modem)
			if line != "":
				logger.info(line.strip())

			if line.startswith("+CMTI"):
				messageIndex = zte.getMessageIndex(line)
				logger.info("Message Index: " + str(messageIndex))
				messageBody = zte.readSMS(modem, messageIndex)
				logger.info("Message Body: " + messageBody.strip())
				zte.deleteSMS(modem, messageIndex)

				if messageBody.lower().startswith("cmd"):
					command = messageBody.split(":")[1].strip()
					logger.info("Command is: " + command)
					
					if command.lower() == "connect":
						connect()
						logger.info("Connected")
						zte.closeModem(modem)
					elif command.lower() == "disconnect":
						disconnect()
						logger.info("Disconnected")
						zte.closeModem(modem)
					elif command.lower() == "ping":
						ping(modem)
						logger.info("Pong")
					elif command.lower() == "reboot":
						reboot()
						logger.info("System going for a reboot")
					elif command.lower() == "status":
						status(modem)
						logger.info("Status reported")
					elif command.lower().startswith("tunnel"):
						tunnelCommandParts = command.split(",")
						if len(tunnelCommandParts) != 4:
							logger.error("Wrong format of open tunnel command")
						else: 
							remotePort = tunnelCommandParts[1]
							localPort = tunnelCommandParts[2]
							address = tunnelCommandParts[3]
							openTunnel(remotePort, localPort, address)
							logger.info("Tunnel opened")
					elif  command.lower() == "closetunnel":
						closeTunnel()
						logger.info("Tunnel closed")
					else:
						logger.info("Unknown command.")
				else:
					logger.info("Error. Invalid command format.")



		zte.closeModem(modem)

	return


if __name__ == '__main__':
	main()
