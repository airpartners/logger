#! /usr/bin/env python3
"""
Connect to a valve to test the interface

Run this script using python's "interactive" flag along with the relevant port for the motor controller's serial connection:

    python3 -i valvetest.py /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_ST13o0a9fm-if00-port0

If it successfully connects to the motor controller, it will wait at a python prompt with `valve` as the relevant BS1010 object defined in `serialdevices.py`,
from which the board can be set

"""

import argparse

from serialdevices import BS1010


parser = argparse.ArgumentParser()
parser.add_argument('valve_port')
# TODO Confirm this is the correct baud for the corresponding serial port.
parser.add_argument('--valve-baud', type=int, required=False, default=9600)
args = parser.parse_args()

valve = BS1010()

# NOTE: reset=False to prevent trying to zero without connected limit switches
valve.connect(port=args.valve_port, baudrate=args.valve_baud, reset=False)
