import serial
from curses import ascii
import time
import logging

logger = logging.getLogger(__name__)

def openModem(modem, time):
	logger.info("Openning " + modem)
	serialPort = serial.Serial(modem, 460800, timeout=5)
	if serialPort.isOpen():
		logger.info("Modem opened.")
		return serialPort
	else:
		logger.error("Could not open modem")
		return -1

def closeModem(modem):
	if modem.isOpen():
		modem.close()
		logger.info("Modem closed.")
	else:
		logger.error("Modem is not opened.")

def checkModem(modem):
	modem.write("AT\r")
	modem.readline()
	status = modem.readline()
	if status.startswith("OK"):
		logger.info("AT OK")
		return True
	else:
		logger.error("AT ERROR")
		return False
				

def setModemTextMode(modem):
	modem.write("AT+CMGF=1\r")
	modem.readline()
	status = modem.readline()
	if status.startswith("OK"):
		logger.info("Modem set in text mode")
		return True
	else:
		return False

def sendSMS(modem, phoneNumber, text):
	modem.write('AT+CMGS="%s"\r' %phoneNumber)
	modem.write(text)
	modem.write(ascii.ctrl('z'))
	time.sleep(2)
	
	modem.readline()
	modem.readline()
	modem.readline()
	cmgi = modem.readline()
	modem.readline()
	modem.readline()
	status = modem.readline()
	if status.startswith("OK"):
		logger.info("SMS sent.")
		return True
	else:
		logger.error("Error sending SMS")
		return False

def deleteSMS(modem, messageIndex):
	modem.write("AT+CMGD=%s\r" %messageIndex)
	modem.readline()
	status = modem.readline()

	if status.startswith("OK"):
		logger.info("SMS deleted")
		return True
	else:
		return False

def readSMS(modem, messageIndex):
	modem.write("AT+CMGR=%s\r" %messageIndex)
	time.sleep(2)

	modem.readline()
	header = modem.readline()
	logger.info(header)
	body = modem.readline()
	modem.readline()
	status = modem.readline()
	logger.info("Status is: " + status.strip())
	if status.startswith("OK"):
		logger.info("SMS read.")
		headerParts = header.split(",")
		if len(headerParts) > 1:
			return "-".join([headerParts[1].strip('"'), body])
		else:
			return body
	else:
		logger.error("Error reading SMS")

def readLineFromModem(modem):
	return modem.readline()

def flushBuffer(modem):
	modem.readlines()

def getMessageIndex(newMessageString):
	newSMSIndicationParts = newMessageString.strip().split(":")
	logger.debug(newSMSIndicationParts[1])
	messageIndex = newSMSIndicationParts[1].split(",")[1]
	logger.debug(messageIndex)
	return messageIndex
