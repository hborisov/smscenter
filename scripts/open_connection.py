#!/usr/bin/python

import subprocess
import os
import sys
import time

def main():
	DEVNULL = open(os.devnull, 'wb')
	try:
	    wvdial = subprocess.Popen(["wvdial", "3gconnect"], stdout=DEVNULL, stderr=DEVNULL)
	except subprocess.CalledProcessError, ex: # error code <> 0 
	    print ex.returncode
	    sys.exit(-1)
	
	DEVNULL.close()
	return wvdial.pid

if __name__ == "__main__":
     wvdialPID = main()
     print wvdialPID
