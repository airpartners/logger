#! /usr/bin/env python3
import argparse
import sys
import time
import logging

from serialdevices import MCPC


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


parser = argparse.ArgumentParser()
parser.add_argument('mcpc_port')
parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
parser.add_argument('--period', type=int, default=10)
parser.add_argument('save_file', type=argparse.FileType, default='-', nargs='?')
args = parser.parse_args()

m = MCPC()
m.connect(args.mcpc_port, args.mcpc_baud)
m._write('help\r\n')
time.sleep(0.5)
eprint(m._read_all())


f = args.save_file
period = args.period
start = time.time()
while True:
    if time.time() - start > period:
        print(m.get_reading(), file=f)
        start = time.time()
    time.sleep(0.1)
