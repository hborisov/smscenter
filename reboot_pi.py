#!/usr/bin/python

import subprocess
import os
import sys

def main():
	DEVNULL = open(os.devnull, 'wb')
	try:
	    result = subprocess.check_call(["sudo", "reboot"],stdout=DEVNULL, stderr=DEVNULL)
	except subprocess.CalledProcessError, ex: # error code <> 0 
	    result = ex.returncode
	
	DEVNULL.close()
	return result

if __name__ == "__main__":
    status = main()
    print status
    sys.exit()
