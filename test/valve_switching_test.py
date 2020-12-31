#!/usr/bin/env python3
"""
Test associated with the three way valve switching functionality.
"""
import os
import sys
import time
from common import get_config
# Grab the dependency from the directory above.
sys.path.append(os.path.realpath('..'))
from serialdevices import ThreeWayValve

def main():
    """
    Connect to the valve and start switching at the rate of the specified
    valve period.
    """
    cfg = get_config()
    valve = ThreeWayValve()
    valve.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)
    valve.open_a()
    valve_period = cfg.valve_period # in seconds
    valve_state = 'a'
    valve_start = time.time()
    while True:
        if time.time() - valve_start > valve_period:
            valve_state = 'a' if valve_state != 'a' else 'b'
            valve.goto_pos(valve_state + '_open')
            valve_start = time.time()
        time.sleep(cfg.sampling_period)

if __name__ == '__main__':
    main()
