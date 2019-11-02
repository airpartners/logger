#!/usr/bin/env python3
import serial
from time import sleep


class MCPC(object):
    """An interface to a Brechtel Mixing Condensation Particle Counter device.

    See: <https://www.brechtel.com/products-item/mixing-condensation-particle-counter/>
    """

    def __init__(self, encoding='utf-8'):
        self.cnxn = None
        self.encoding = encoding

    def connect(self, port, baudrate=115200, timeout=2, **kwargs):
        """Connect to the device over serial."""
        self.cnxn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, **kwargs)

    def close(self):
        """Close the serial connection."""
        self.cnxn.close()

    def send_cmd(self, cmd: str):
        """Write a serial command to the device."""
        self.cnxn.write(cmd.encode(self.encoding) + b'\r\n')

    def _read(self, num_bytes: int = 64) -> str:
        return self.cnxn.read(num_bytes).decode(self.encoding)

    def read_all(self) -> str:
        """Read all data returned by the device."""
        buf = ''
        while self.cnxn.in_waiting > 0:
            buf += self.cnxn.read().decode(self.encoding)
        return buf

    @staticmethod
    def _parse_values(data: str):
        """Parse values returned by the device.

        >>> MCPC._parse_values('satfpwr=0  \\rfillcnt=0     \\rerr_num=0    \\r\\r')
        {'satfpwr': '0', 'fillcnt': '0', 'err_num': '0'}
        """
        res = {}
        for l in filter(lambda s: s != '', data.splitlines()):
            try:
                k, v = l.strip().split('=')
            except ValueError:
                raise serial.SerialException("Couldn't parse data {!r}".format(l))
            else:
                res[k] = v

        return res

    def get_reading(self):
        self.send_cmd('read')
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)


    def get_settings(self):
        self.send_cmd('settings')
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)
