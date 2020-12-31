#! /usr/bin/env python3
"""
MCPC logger test code - connects to and prints readings from the logger.
"""
import os
import sys
import time
from common import get_config
# Grab the dependency from the directory above.
sys.path.append(os.path.realpath('..'))
from serialdevices import MCPC

def main():
    """
    Connect to the mcpc and print readings at the sampling period.
    """
    cfg = get_config()
    mcpc = MCPC()
    mcpc._write('help\r\n')
    time.sleep(0.5)
    save_file = cfg.save_file
    sampling_period = cfg.sampling_period
    sampling_start = time.time()
    while True:
        if time.time() - sampling_start > sampling_period:
            print(mcpc.get_reading(), file=save_file)

if __name__ == '__main__':
    main()
