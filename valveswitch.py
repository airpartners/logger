#!/usr/bin/env python3
"""Switch a three-way valve between postions."""
import argparse
import time

from serialdevices import ThreeWayValve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('valve_port')
    parser.add_argument('--valve-baud', type=int, required=False, default=9600)
    parser.add_argument('period', type=int)
    args = parser.parse_args()

    valve = ThreeWayValve()
    valve.connect(port=args.valve_port, baudrate=args.valve_baud)

    period = args.period
    is_a = True  # start with a valve
    start = time.time()
    valve.open_a()
    print('a')
    while True:
        if time.time() - start > period/2:
            is_a = not is_a
            which_one = 'a' if is_a else 'b'
            start = time.time()
            valve.open_a() if which_one == 'a' else valve.open_b()
            print(which_one)
            # valve.wait_for_idle()
            # print('done')
        time.sleep(0.1)


if __name__ == '__main__':
    main()
