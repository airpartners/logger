#!/usr/bin/env python3
import argparse
import datetime
import os
import time
import logging
import logging.handlers

from serialdevices import MCPC, ThreeWayValve


values = [
    ('MCPC_PORT', str, None),
    ('MCPC_BAUD', int, 38400),
    ('VALVE_PORT', str, None),
    ('VALVE_BAUD', int, 9600),
    ('VALVE_PERIOD', int, 10),
    ('SAMPLING_PERIOD', int, 1),
    ('SAVE_FILE', str, 'data.csv'),
]


def get_config():
    ns = argparse.Namespace()
    for name, modifier, default in values:
        val = os.getenv(name, default)
        if val is None:
            raise ValueError('Required Environment variable {!r} is not set!'.format(name))
        setattr(ns, name.lower(), modifier(val))
    return ns


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--mcpc_port', required=True)
    # parser.add_argument('--mcpc-baud', type=int, required=False, default=115200)
    # parser.add_argument('--log-period', type=int, required=False, default=1)
    # parser.add_argument('--valve-port', required=True)
    # parser.add_argument('--valve-baud', type=int, required=False, default=9600)
    # parser.add_argument('--valve-period', type=int, required=False, default=5)
    # parser.add_argument('savefile', type=argparse.FileType('w'), default='-', nargs='?')

    cfg = get_config()

    m = MCPC()
    m.connect(port=cfg.mcpc_port, baudrate=cfg.mcpc_baud)

    valve = ThreeWayValve()
    valve.connect(port=cfg.valve_port, baudrate=cfg.valve_baud)

    data_logger = logging.Logger('data')
    data_logger.setLevel(logging.INFO)
    file_handler = logging.handlers.TimedRotatingFileHandler(cfg.save_file, when='D', interval=1)
    data_logger.addHandler(file_handler)
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # write header
    mcpc_data = m.get_reading()
    data = {'timestamp': None, 'valve': None}
    data.update(mcpc_data)
    data_logger.info(','.join(map(str, data.keys())))

    valve.open_a()
    valve_period = cfg.valve_period # in seconds
    valve_state = 'a'
    valve_start = time.time()
    while True:
        timestamp = datetime.datetime.now().isoformat()
        mcpc_data = m.get_reading()
        data = {'timestamp': timestamp, 'valve': valve_state}
        data.update(mcpc_data)
        # print(data)
        data_logger.info(','.join(map(str, data.values())))
        if time.time() - valve_start > valve_period:
            valve_state = 'a' if valve_state != 'a' else 'b'
            valve.goto_pos(valve_state + '_open')
            valve_start = time.time()
        time.sleep(cfg.sampling_period)


if __name__ == '__main__':
    main()
