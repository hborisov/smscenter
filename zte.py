import serial

def openModem(modem, time):
	print "Openning " + modem
	serialPort = serial.Serial(modem, 460800, timeout=5)
	print serialPort
	print serialPort.isOpen
	if serialPort.isOpen():
		return serialPort
	else:
		print "Could not open modem"
		return -1

def closeModem(modem):
	if modem.isOpen():
		modem.close()
	else:
		print "Modem is not opened."

def checkModem(modem):
	modem.write("AT\r")
	modem.readline()
	status = modem.readline()
	if status.startswith("OK"):
		return True
	else:
		return False
				

def setModemTextMode(modem):
	modem.write("AT+CMGF=1\r")
	modem.readline()
	status = modem.readline()
	if status.startswith("OK"):
		return True
	else:
		return False

