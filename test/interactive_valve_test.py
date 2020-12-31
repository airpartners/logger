#! /usr/bin/env python3
"""
Connect to a valve to test the interface and quickly run commands.

Run this script using python's "interactive" flag along with the relevant port
for the motor controller's serial connection:

python3 -i valvetest.py /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_ST13o0a9fm-if00-port0

If it successfully connects to the motor controller, it will wait at a python
prompt with `valve` as the relevant BS1010 object defined in `serialdevices.py`
which sets the board in the first place.

This test does not use the environment-variable based approach, and is
especially useful when trying to debug the motor without explicitly considering
the serial connection.
"""
import argparse
import os
import sys

# Grab the dependency from the directory above.
sys.path.append(os.path.realpath('..'))
from serialdevices import ThreeWayValve

def main():
    """
    Main method associatd with connecting to the valve and starting a console.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('valve_port')
    parser.add_argument('--valve-baud', type=int, required=False, default=9600)
    args = parser.parse_args()

    valve = ThreeWayValve()

    # NOTE: reset=False to prevent trying to zero without connected limit switches
    valve.connect(port=args.valve_port, baudrate=args.valve_baud, reset=False)

if __name__ == '__main__':
    main()
