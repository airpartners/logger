#!/usr/bin/env python3
import argparse
import datetime
import os
import time

from serialdevices import MCPC, ThreeWayValve


values = [
    ('MCPC_PORT', str),
    ('MCPC_BAUD', int),
    ('VALVE_PORT', str),
    ('VALVE_BAUD', int),
    ('SAVE_FILE', str),
]


def get_env_value(name, modifier):
    val = os.getenv(name, None)
    if val is None:
        return None
    return modifier(val)


def get_config():
    ns = argparse.Namespace()
    for name, modifier in values:
        val = get_env_value(name, modifier)
        ns[name] = val
    return ns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcpc_port', required=True)
    parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
    parser.add_argument('--log-period', type=int, required=False, default=1)
    parser.add_argument('--valve-port', required=True)
    parser.add_argument('--valve-baud', type=int, required=False, default=9600)
    parser.add_argument('--valve-period', type=int, required=False, default=5)
    parser.add_argument('savefile', type=argparse.FileType('w'), default='-', nargs='?')
    args = parser.parse_args()


    m = MCPC()
    m.connect(port=args.mcpc_port, baudrate=args.mcpc_baud)

    valve = ThreeWayValve()
    valve.connect(port=args.valve_port, baudrate=args.valve_baud)

    f = args.savefile

    valve.open_a()
    valve_period = args.valve_period # in seconds
    valve_state = 'a'
    valve_start = time.time()
    while True:
        mcpc_data = m.get_reading()
        timestamp = datetime.datetime.now().isoformat()
        data = {'timestamp': timestamp, 'valve': valve_state}
        data.update(mcpc_data)
        print(data, file=f)
        if time.time() - valve_start > valve_period:
            valve_state = 'a' if valve_state != 'a' else 'b'
            valve.goto_pos(valve_state + '_open')
            valve_start = time.time()
        time.sleep(args.log_period)


if __name__ == '__main__':
    main()
