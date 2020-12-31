#! /usr/bin/env python3
"""
Common functions and data structures used in the context of testing
components of the sensor box.
"""

import argparse
import os

# Default set of values to configure, and some of their default values.
VALUES = [
    ('MCPC_BAUD', int, 38400),
    ('MCPC_PORT', str, None),
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
    current_ns = argparse.Namespace()
    for name, modifier, default in VALUES:
        val = os.getenv(name, default)
        if val is None:
            raise ValueError('Required Environment variable {!r} is not set!'.format(name))
        setattr(current_ns, name.lower(), modifier(val))
    return current_ns