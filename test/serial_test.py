#! /usr/bin/env python3
"""
Launch and debug using the serial connection to the valve by connecting to the
valve and opening a connection for sending and receiving commands.
This program takes a command line argument, where the argument 'valve' connects
to the valve and the argument 'mcpc' connects to the MCPC.
"""
import argparse
import os
import sys
import time

from common import get_config

# Grab the dependency from the directory above.
sys.path.append(os.path.realpath('..'))
from serialdevices import SerialDevice

def main():
    """
    Connect to the specified device so that the tester can send commands to it.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('Device', type=str, help="Specify which device (either" \
                        "valve or mcpc) to connect to.")
    cfg = get_config()
    device = SerialDevice(encoding='ASCII')

    # Parse the input argument to determine which device to connect to.
    args = parser.parse_args()
    if args.Device == "valve":
        device.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)
    elif args.Device == "mcpc":
        device.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)
    else:
        print("Please specify whether to connect to the valve or mcpc.")
        return

    # Set up a command line interface.
    try:
        while True:
            cmd = input('cmd: ')
            device._write(cmd + '\n')
            time.sleep(0.1)
            print('\n'.join(map(repr, device.read_all().splitlines(keepends=True))))
    except (KeyboardInterrupt, EOFError):
        pass

if __name__ == '__main__':
    main()
