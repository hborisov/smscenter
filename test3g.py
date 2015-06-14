#!/usr/bin/python

import zte

modem = zte.openModem("/dev/ttyUSB1", 5)
if modem != -1:
	print zte.checkModem(modem)
	zte.closeModem(modem)
