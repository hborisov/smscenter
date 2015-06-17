#!/usr/bin/python
import serial
import time
import subprocess
import os
import signal
from curses import ascii
from zte import zte
import logging
import logging.config
import ConfigParser
import sys
from os.path import dirname

pid = -1
child = None
tunnelchild = None


BASEDIR = dirname(sys.argv[0])
print BASEDIR

logging.config.fileConfig(BASEDIR + '/logging_config.ini')
logger = logging.getLogger('smsserver')

config = ConfigParser.SafeConfigParser()
config.read(BASEDIR + '/smsserver.conf')


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
			global BASEDIR
			connectionpid = open(BASEDIR + '/connection.pid', 'w')
			connectionpid.write(str(child.pid))
		except subprocess.CalledProcessError, ex: # error code <> 0 
			logger.info("Error starting wvdial.")
	    		logger.info(ex.returncode)
	    		return -1
	else:
		logger.info("Connection is already opened.")


def disconnect():
	logger.info("Disconnecting...")

	global child
	if child != None:
		logger.info("closing: " + str(child.pid))
		child.terminate()	
		child.wait()	
	else:
		logger.info('Disconnecting by pid')

		global BASEDIR
		connectionpid = open(BASEDIR + '/connection.pid', 'r')
		pid = connectionpid.read()
		logger.info('pid is %s' % str(pid))
		os.kill(int(pid), signal.SIGTERM)
		time.sleep(3)
		try:
			os.kill(int(pid), 0)
			os.kill(int(pid), signal.SIGKILL)
			os.kill(int(pid), 0)
		except Exception, e:
			logger.info('process successfully killed')
			connectionpid.close()
			os.remove(BASEDIR + '/connection.pid')


def ping(modem, sender):
	logger.info("Pong...")

	zte.sendSMS(modem, sender, "pong")

def reboot():
	logger.info("Rebooting...")
	subprocess.call(["sudo", "/sbin/reboot"])

def status(modem, sender):
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
	logger.info(zte.sendSMS(modem, sender, statusText))

def openTunnel(remotePort, localPort, toAddress, password):
	portSpecification = "%s:localhost:%s" % (remotePort, localPort)
	logger.info("Opening tunnel to: " + portSpecification)

	DEVNULL = open(os.devnull, 'wb')
	try:
		global tunnelchild
		tunnelchild = subprocess.Popen(['sshpass', '-p', password, 'ssh', '-nNT', '-R', portSpecification, toAddress], stdout=DEVNULL, stderr=DEVNULL)

		pidfile = open(BASEDIR + '/tunnel.pid', 'w')
		pidfile.write(str(tunnelchild.pid))
		pidfile.close()

	except subprocess.CalledProcessError, ex:
		logger.exception(ex)
		return ex.returncode

	logger.info("Tunnel opened")

def closeTunnel():
	logger.info("Closing tunnel")

	global tunnelchild
	if tunnelchild != None:
		tunnelchild.terminate()
		tunnelchild.wait()
	else:
		pidfile = open(BASEDIR + '/tunnel.pid', 'r')
		pid = pidfile.read()
		logger.info('Tunnel pid is %s' % str(pid))

		os.kill(int(pid), signal.SIGTERM)
		time.sleep(3)
		try:
			os.kill(int(pid), 0)
			os.kill(int(pid), signal.SIGKILL)
			os.kill(int(pid), 0)
		except Exception, e:
			logger.info('Tunnel successfully killed')
			connectionpid.close()
			os.remove(BASEDIR + '/tunnel.pid')

	
def openModem():
	usbPort = config.get('main', 'usb_port')
	modem = zte.openModem(usbPort, 5)
	if modem != -1:
		logger.info(zte.flushBuffer(modem))
		zte.setModemTextMode(modem)
	
	return modem

def checkSender(sender):
	global notificationList
        if sender not in notificationList:
                logger.error("Sender not in notification list. Aborting")
                return False

	return True


def main():
	modem = openModem()
	global notificationList
	sendGreetings = config.getboolean("main", "send_greetings")
	if sendGreetings:
		for recepient in notificationList:
			zte.sendSMS(modem, recepient, 'Pi is online. Waiting for commands.')

	while True:
		try:
			isOpen = modem.isOpen()
			logger.debug("Modem is open? %s" % isOpen)
			if not isOpen:
				modem = openModem()

			line = zte.readLineFromModem(modem)
			if line != "":
				logger.info(line.strip())

			if line.startswith("+CMTI"):
				messageIndex = zte.getMessageIndex(line)
				logger.info("Message Index: " + str(messageIndex))
				messageHeaderAndBody = zte.readSMS(modem, messageIndex)
				logger.info("Message Body: " + messageHeaderAndBody.strip())
				zte.deleteSMS(modem, messageIndex)
					
				if "-" in messageHeaderAndBody:
					sender = messageHeaderAndBody.split("-")[0]
					if not checkSender(sender):
						continue

					messageBody = messageHeaderAndBody.split("-")[1]
				else:
					messageBody = messageHeaderAndBody

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
						ping(modem, sender)
						logger.info("Pong")
					elif command.lower() == "reboot":
						reboot()
						logger.info("System going for a reboot")
					elif command.lower() == "status":
						status(modem, sender)
						logger.info("Status reported")
					elif command.lower().startswith("tunnel"):
						tunnelCommandParts = command.split(",")
						if len(tunnelCommandParts) != 5:
							logger.error("Wrong format of open tunnel command")
						else: 
							remotePort = tunnelCommandParts[1]
							localPort = tunnelCommandParts[2]
							address = tunnelCommandParts[3]
							password = tunnelCommandParts[4]
							openTunnel(remotePort, localPort, address, password)
							logger.info("Tunnel opened")
					elif  command.lower() == "closetunnel":
						closeTunnel()
						logger.info("Tunnel closed")
					else:
						logger.info("Unknown command.")
				else:
					logger.info("Error. Invalid command format.")


		except Exception, e:
			logger.exception(e)
			time.sleep(5)
			zte.closeModem(modem)
			continue
	
	zte.closeModem(modem)
	return


if __name__ == '__main__':
	global notificationList
	notificationList = config.get("main", "notification_list").split(",")
	main()

