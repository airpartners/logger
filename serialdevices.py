import serial
import time


class SerialDevice(object):
    def __init__(self, encoding='utf-8'):
        self.cnxn = None
        self.encoding = encoding

    def connect(self, port, baudrate, timeout=2, **kwargs):
        """Connect to the device over serial."""
        self.cnxn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, **kwargs)

    def close(self):
        """Close the serial connection."""
        self.cnxn.close()

    def _read(self, num_bytes: int = 64) -> str:
        return self.cnxn.read(num_bytes).decode(self.encoding)

    def read_all(self) -> str:
        """Read all data returned by the device."""
        buf = ''
        while self.cnxn.in_waiting > 0:
            buf += self.cnxn.read().decode(self.encoding)
        return buf

    def _write(self, msg: str):
        """Write a serial command to the device."""
        self.cnxn.write(msg.encode(self.encoding))

    def assert_response(self, msg):
        response = self.read_all()
        if msg not in response:
            raise serial.SerialException('Device did not return {!r}')

    def wait_for(self, msg, timeout=2) -> str:
        start = time.time()
        buffer = ''
        while time.time() - start < timeout:
            if self.cnxn.in_waiting > 0:
                buffer += self.cnxn.read().decode(self.encoding)
                if msg in buffer:
                    return buffer
        raise serial.SerialTimeoutException('Device timed out waiting for msg: {!r}'.format(msg))


class MCPC(SerialDevice):
    """An interface to a Brechtel Mixing Condensation Particle Counter device.

    See: <https://www.brechtel.com/products-item/mixing-condensation-particle-counter/>
    """

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

    def send_cmd(self, cmd):
        self._write(cmd + '\r\n')

    def get_reading(self):
        self.send_cmd('read')
        time.sleep(0.1)
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)

    def get_settings(self):
        self.send_cmd('settings')
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)


class BS1010(SerialDevice):
    """An interface to a Brechtel Mixing Condensation Particle Counter device.

    See: <https://www.brechtel.com/products-item/mixing-condensation-particle-counter/>
    """

    width = 2000  # rough range of motion from -X to +X limit switch

    def __init__(self):
        super().__init__(encoding='ascii')
        self.xpos = None

    def connect(self, port, baudrate, timeout=2, reset=True, **kwargs):
        super().connect(port, baudrate, timeout=timeout, **kwargs)
        if reset:
            # reset device and init state
            self.reset()

    def goto(self, pos: int):
        """Note: this returns when it has acknowledged the move, not when finished moving."""
        self.send_cmd(str(pos) + 'G')
        self.wait_for_ack()

    def get_pos(self):
        self.send_cmd('-1?')
        return int(self.wait_for_ack()[:-1].strip().split(',')[2])

    def set_pos(self, pos: int):
        self.send_cmd(str(pos) + '=')
        self.wait_for_ack()

    def wait_for_ack(self, timeout=0.5):
        return self.wait_for('*', timeout=timeout)

    def wait_for_idle(self, timeout=5):
        self.send_cmd('I')
        self.wait_for_ack(timeout=timeout)

    def report_latches(self):
        # TODO: make this clearer
        self.send_cmd('L')
        resp = self.wait_for_ack()
        resp = resp[:-1].strip()
        _, value = resp.split(',')
        return int(value)

    def reset(self):
        self.cnxn.flush()
        self.send_cmd('!')  # reset command
        self.wait_for_ack()
        l = self.report_latches()
        assert l & 16

        # zero the thing
        self.send_cmd('X')  # set motion to x-axis
        self.goto(-(self.width + 1000))
        self.wait_for_idle()
        l = self.report_latches()
        assert l & 4
        self.set_pos(-100)
        self.goto(0)
        self.wait_for_idle()

    def send_cmd(self, cmd):
        self._write(cmd)

    def set_runspeed(self, speed: int = 800):
        self.send_cmd(str(speed) + 'R')
        self.wait_for_ack()


class ThreeWayValve(BS1010):
    positions = {
        'a_open': 0,
        'b_open': 2000,
        'both': 1000,
    }
    speed = 3200

    def reset(self):
        super().reset()
        self.set_runspeed(self.speed)

    def goto_pos(self, pos: str):
        """Move to a named position from self.positions"""
        self.goto(self.positions[pos])

    def open_a(self):
        self.goto_pos('a_open')

    def open_b(self):
        self.goto_pos('b_open')
