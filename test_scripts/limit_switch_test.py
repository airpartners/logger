#!/usr/bin/env python3
"""
Test for testing the valve limit switch.
"""

import argparse
import os
import time

from serialdevices import ThreeWayValve

VALUES = [
    ('VALVE_PORT', str, None),
    ('VALVE_BAUD', int, 9600),
]

def get_config():
    """
    Get the configuration information from the environment variables associated
    with the namespace.
    """
    current_ns = argparse.Namespace()
    for name, modifier, default in VALUES:
        val = os.getenv(name, default)
        if val is None:
            raise ValueError('Required Environment variable {!r} is not set!'.format(name))
        setattr(current_ns, name.lower(), modifier(val))
    return current_ns

def main():
    """
    Main method associatd with simply connecting and then switching the valve.
    """
    cfg = get_config()
    valve = ThreeWayValve()
    valve.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)
    valve_period = cfg.valve_period # in seconds
    valve_start = time.time()
    while True:
        if time.time() - valve_start > valve_period:
            l = valve.report_latches()
            print(l)
        time.sleep(cfg.sampling_period)

if __name__ == '__main__':
    main()
