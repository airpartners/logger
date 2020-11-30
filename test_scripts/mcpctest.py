#! /usr/bin/env python3
import argparse
import sys
import time

from serialdevices import MCPC

"""
MCPC logger test code, used for debugging.
"""

def eprint(*args, **kwargs):
    """
    Print error associated with MCPC logger.
    """
    print(*args, file=sys.stderr, **kwargs)


parser = argparse.ArgumentParser()
parser.add_argument('mcpc_port')
parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
parser.add_argument('--period', type=int, default=1)
parser.add_argument('save_file', type=argparse.FileType('w'), default='-', nargs='?')
args = parser.parse_args()

m = MCPC()
m.connect(args.mcpc_port, args.mcpc_baud)
m._write('help\r\n')
time.sleep(0.5)
eprint(m.read_all())


f = args.save_file
period = args.period
start = time.time()
def get_reading():
    print(m.get_reading(), file=f)

