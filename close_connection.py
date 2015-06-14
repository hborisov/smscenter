#!/usr/bin/python

import subprocess
import os
import sys
import time
import signal

def main(arguments):
	pid = int(arguments[1])
	print pid
	os.kill(pid, signal.SIGTERM)

if __name__ == "__main__":
	main(sys.argv)
