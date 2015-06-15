#!/usr/bin/python

import zte

modem = zte.openModem("/dev/ttyUSB1", 5)
if modem != -1:
	print zte.checkModem(modem)
	print zte.setModemTextMode(modem)
	print zte.sendSMS(modem, "0882506400", "test")


	zte.closeModem(modem)
