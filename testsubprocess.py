#!/usr/bin/python

import os
import subprocess
import time

DEVNULL = open(os.devnull, 'wb')
global child
child = subprocess.Popen(["wvdial", "3gconnect"], stdout=DEVNULL, stderr=DEVNULL)

time.sleep(5)

child.terminate()
