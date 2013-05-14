#!/usr/bin/python
"""Try and print my IP address"""

import socket

from Printer import *

# Printer setup
DEVICE_NAME = Printer
LOCATION = "/dev/ttyAMA0"
BAUD_RATE = 19200
TIMEOUT = 5

printer = DEVICE_NAME(LOCATION, BAUD_RATE, timeout=TIMEOUT)

# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting.
time.sleep(30)

# Show IP address (if network is available)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('capture.local', 0))
    printer.println('The server is online.')
    printer.println('IP address is ' + s.getsockname()[0])
    printer.feed(5)
except:
    printer.boldOn()
    printer.println('The server is offline.')
    printer.boldOff()
    printer.println('Photos will be stored locally.')
    printer.feed(5)
    exit(0)
