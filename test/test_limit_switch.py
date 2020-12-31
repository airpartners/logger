#!/usr/bin/env python3
"""
Test for testing the valve limit switch. Currently just prints the latches variable
associated with the limit switch, which changes based on the limit switch
configuration and status.
"""

import argparse
import os
import sys
import time

from common import get_config
# Grab the dependency from the directory above.
sys.path.append(os.path.realpath('..'))
from serialdevices import ThreeWayValve

def main():
    """
    Main method associatd with connecting to the valve and printing the
    latches status associated with the valve.
    """
    cfg = get_config()
    valve = ThreeWayValve()
    valve.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)
    valve_period = 0.5 # This value is in seconds.
    valve_start = time.time()
    while True:
        if time.time() - valve_start > valve_period:
            l = valve.report_latches()
            print(l)
        time.sleep(valve_period)

if __name__ == '__main__':
    main()
