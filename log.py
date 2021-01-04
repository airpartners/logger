#!/usr/bin/env python3
"""
Log data from the mcpc to the given save file. This program does not use
environment variables - instead, just pass the values for the MCPC port,
the expected baudrate (if not default), and the savefile. This will
continuously write the raw MCPC data to the file, so it will remain loosely
formatted raw input.
"""

import argparse
import sys
from time import sleep
from serialdevices import MCPC

def main():
    """
    Log MCPC data to the save file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('mcpc_port')
    parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
    parser.add_argument('save_file', type=argparse.FileType('w'), default=sys.stdout, nargs='?')
    parser.add_argument('--period', type=int, required=False, default='1')
    args = parser.parse_args()
    
    # Create and configure the mcpc instance.
    m = MCPC()
    m.connect(port=args.mcpc_port, baudrate=args.mcpc_baud)
    f = args.savefile

    # Log the raw data indefinitely.
    while True:
        data = m.get_reading()
        f.write(data)
        sleep(args.period)

if __name__ == '__main__':
    main()
