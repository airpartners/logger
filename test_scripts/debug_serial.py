#! /usr/bin/env python3


import argparse
import time

from serialdevices import SerialDevice

parser = argparse.ArgumentParser()
parser.add_argument('port', type=str)
parser.add_argument('baud', type=int)

args = parser.parse_args()

PORT: str = args.port
BAUD: int = args.baud

s = SerialDevice(encoding='ASCII')

s.connect(PORT, BAUD)

try:
    while True:
        cmd = input('cmd: ')
        s._write(cmd + '\n')
        time.sleep(0.1)
        print('\n'.join(map(repr, s.read_all().splitlines(keepends=True))))
except (KeyboardInterrupt, EOFError):
    pass
