#!/usr/bin/env python3
import argparse
from time import sleep

from serialdevices import MCPC


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mcpc_port')
    parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
    parser.add_argument('savefile', type=argparse.FileType, default='-', nargs='?')
    args = parser.parse_args()
    # import pdb; pdb.set_trace()

    m = MCPC()
    m.connect(port=args.mcpc_port, baudrate=args.mcpc_baud)

    f = args.savefile
    while True:
        data = m.get_reading()
        f.write(data)
        sleep(1)


if __name__ == '__main__':
    main()
