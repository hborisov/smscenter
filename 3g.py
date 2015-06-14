import serial

def openModem(modem, time):
	serialPort = serial.Serial(modem, 460800, timeout=time)
	if serialPort.isOpen == True:
		return serialPort
	else:
		return -1

def closeModem(modem):
	if modem.isOpen == True:
		modem.close()
	else
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

