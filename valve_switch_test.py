#!/usr/bin/env python3

import argparse
import datetime
import os
import time
import logging
import logging.handlers

from serialdevices import MCPC, ThreeWayValve

values = [
    ('MCPC_BAUD', int, 38400),
    ('VALVE_PORT', str, None),
    ('VALVE_BAUD', int, 9600),
    ('VALVE_PERIOD', int, 10),
    ('SAMPLING_PERIOD', int, 1),
    ('SAVE_FILE', str, 'data.csv'),
]

def get_config():
    """
    Get the configuration information from the environment variables associated
    with the namespace.
    """
    ns = argparse.Namespace()
    for name, modifier, default in values:
        val = os.getenv(name, default)
        if val is None:
            raise ValueError('Required Environment variable {!r} is not set!'.format(name))
        setattr(ns, name.lower(), modifier(val))
    return ns

def main():
    """
    Main method associatd with simply connecting and then switching the valve.
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
