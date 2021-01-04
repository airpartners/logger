#! /usr/bin/env python3
"""
Log data from the mcpc to the given save file. This program does not use
environment variables - instead, just pass the values for the MCPC port,
the expected baudrate (if not default), and the savefile. This will
continuously write the raw MCPC data to the file, so it will remain loosely
formatted raw input.
"""
import argparse
import sys
import time
import logging

from serialdevices import MCPC


def eprint(*args, **kwargs):
    """
    Print MCPC logger info to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)

def main():
    """
    Wite raw MCPC data to the save file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('mcpc_port')
    parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
    parser.add_argument('--period', type=int, default=1)
    parser.add_argument('save_file', type=argparse.FileType('w'), default='-', nargs='?')
    args = parser.parse_args()
    
    # Create and configure the mcpc instance.
    m = MCPC()
    m.connect(args.mcpc_port, args.mcpc_baud)
    m._write('help\r\n')
    time.sleep(0.5)
    eprint(m.read_all())

    # Log the raw data indefinitely.
    f = args.save_file
    period = args.period
    start = time.time()
    while True:
        if time.time() - start > period:
            print(m.get_reading(), file=f)
            start = time.time()
        time.sleep(0.1)

if __name__ == '__main__':
    main()
