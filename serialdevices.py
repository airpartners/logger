"""
This file contains the source for the base SerialDevice and specific device
implementations.
"""
import serial
import time

class SerialDevice(object):
    """
    General interface to connect to a device over serial.
    Individual devices should extend this interface for specific functionality.
    """
    def __init__(self, encoding='utf-8'):
        """
        Initialize basic parameters associated with the serial device.
        encoding : The encoding associated with data sent over the channel.
                   Defaults to utf-8.
        """
        # The Serial connection associated with the device.
        self.cnxn = None
        # The encoding associated with the serial channel, defaults to utf-8.
        self.encoding = encoding
        # If serial device connection fails outright (i.e. does not get stuck
        # waiting but fails in the first place), set this flag.
        self.started_connection = False
        # Default timeout for serial connection.
        # If connection, etc. specifies 0 as the timeout, the class will
        # default to this instead.
        self.default_timeout = 10

    def get_started_connection(self):
        """
        Returns whether connection has started (i.e. no exceptions or errors
        when instantiating the Serial device. Could still fail due to timeout
        or data quality issues; this is an initial check.
        """
        return self.started_connection

    def get_default_timeout(self):
        """
        Return default timeout value of the serial connection interface.
        """
        return self.default_timeout

    def connect(self, port, baudrate, timeout=0, **kwargs):
        """
        Connect to the device over serial.
        Prints if connection
        """
        try:
            if timeout == 0:
                timeout = self.default_timeout
            # This will throw an error if the connection fails.
            self.cnxn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, **kwargs)
            self.started_connection = True
        except:
            self.started_connection = False
            print("Failed to connect to device.")

    def close(self):
        """
        Close the serial connection.
        """
        self.cnxn.close()

    def _read(self, num_bytes: int = 64) -> str:
        """
        Read
        num_bytes: The int number of bytes to read, defaults to 64.
        Returns string of data read (length num_bytes).
        """
        return self.cnxn.read(num_bytes).decode(self.encoding)

    def read_all(self) -> str:
        """
        Read all data returned by the device.
        Returns string of data read (returns entire buffer).
        """
        buf = ''
        while self.cnxn.in_waiting > 0:
            buf += self.cnxn.read().decode(self.encoding)
        return buf

    def _write(self, msg: str):
        """
        Write a serial command to the device.
        msg: String command to write to the device.
        """
        self.cnxn.write(msg.encode(self.encoding))

    def assert_response(self, msg):
        """
        Raises an exception if specified msg is not in response.
        msg : String expected within response
        """
        response = self.read_all()
        if msg not in response:
            raise serial.SerialException('Device did not return {!r}')

    def wait_for(self, msg, timeout=0) -> str:
        """
        Wait for a specific message response for a specific amount of time.
        msg: String message to wait for (potentially as part of larger output).
        timeout: int number of seconds to wait for.
        Returns full received buffer as a str.
        """
        start = time.time()
        buffer = ''
        if timeout == 0:
            timeout = self.default_timeout
        while time.time() - start < timeout:
            if self.cnxn.in_waiting > 0:
                buffer += self.cnxn.read().decode(self.encoding)
                if msg in buffer:
                    return buffer
        raise serial.SerialTimeoutException('Device timed out waiting for msg: {!r}'.format(msg))


class MCPC(SerialDevice):
    """
    Interface to a Brechtel Mixing Condensation Particle Counter device.
    Documentation at https://github.com/airpartners/logger/wiki/hardware-overview.
    """
    def __init__(self, response_wait_time=0.2):
        """
        Initialize the MCPC with SerialDevice parameters and a measurement delay.
        """
        super().__init__()
        # Time in seconds to wait between sending a command and attempting to read the response.
        # Default of .2 set via empirical testing and can be adjusted as needed.
        self.response_wait_time = response_wait_time

    @staticmethod
    def _parse_values(data: str):
        """
        Parse values returned by the device.
        Execution looks like the following:
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
        """
        Write a specific command to the MCPC.
        cmd: The string command to write to the MCPC.
        """
        self._write(cmd + '\r\n')

    def get_reading(self):
        """
        Send the read command to the device, and return the received data.
        Returns parsed dictionary of values. Prints if the device
        receives no data.
        """
        self.send_cmd('read')
        time.sleep(self.response_wait_time)
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)

    def get_all(self):
        """
        Get all values from the MCPC logger.
        Returns parsed dictionary of all values. Prints if the device
        receives no data.
        """
        self.send_cmd('all')
        time.sleep(self.response_wait_time)
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)

    def get_settings(self):
        """
        Get the current settings associatd with the MCPC device.
        Returns parsed dictionary of all settings. Prints if the device
        receives no data.
        """
        self.send_cmd('settings')
        time.sleep(self.response_wait_time)
        resp = self.read_all()
        assert len(resp) > 0, "Device returned no data"
        return self._parse_values(resp)

    def get_response_wait_time(self):
        """
        Returns the (floating-point) response wait time associated with the
        device (i.e. the set amount of time each method waits after sending
        a command to read the response).
        """
        return self.response_wait_time

    def set_response_wait_time(self, response_wait_time):
        """
        Set the (floating-point) response wait time associated with the
        device (i.e. the set amount of time each method waits after sending
        a command to read the response).
        """
        self.response_wait_time = response_wait_time

class BS1010(SerialDevice):
    """
    An interface to a BS1010 Stepper Motor Controller from Peter Norberg Consulting, Inc.
    Specifically, this is designed around controlling the x-axis of the board,
    so it will need to vary for boards with different connector configurations.
    Board documentation at https://github.com/airpartners/logger/wiki/hardware-overview.
    """
    # Rough range of motion from -X to +X limit switch.
    width = 2000

    def __init__(self):
        """
        Initialize the device with a blank xposition and ascii encoding.
        """
        super().__init__(encoding='ascii')
        # The current x position (as understood by the program).
        # TODO This would be useful for debugging, see issue 11.
        self.xpos = None

    def connect(self, port, baudrate, timeout=0, reset=True, **kwargs):
        """
        Connect to the board, and then zero the device.
        """
        super().connect(port, baudrate, timeout=timeout, **kwargs)
        # Reset and zero the device on connection.
        if reset:
            self.reset()

    def goto(self, pos: int):
        """
        Go to the specified numerical position value.
        Note: Returns when it has acknowledged the move, not when done moving.
        pos: int position to go to. Should be within width.
        """
        self.send_cmd(str(pos) + 'G')
        self.wait_for_ack()

    def get_pos(self):
        """
        Returns the current position value, as understood by the board.
        Returns int position values, with X position followed by Y position.
        """
        self.send_cmd('-1?')
        return int(self.wait_for_ack()[:-1].strip().split(',')[2])

    def set_pos(self, pos: int):
        """
        Set the position of the motor, as specified by pos. Note that this will
        not actually mov ethe motion, just change the current understanding of
        the posiion.
        pos : int value for the position of the motor. Should be within width.
        """
        self.send_cmd(str(pos) + '=')
        self.wait_for_ack()

    def wait_for_ack(self, timeout=1):
        """
        Wait for the acknowledgement response over the serial connection.
        timeout: int number of seconds to wait for execution.
        """
        return self.wait_for('*', timeout=timeout)

    def wait_for_idle(self, timeout=5):
        """
        Waits for the motor to become idle after moving.
        timeout: int number of seconds to wait for execution. Note that this
                 will need to increase with higher speeds.
        """
        self.send_cmd('I')
        self.wait_for_ack(timeout=timeout)

    def report_latches(self):
        """
        Return limit switch status. See page 43 in the BS1010 manual in the
        hardware overview section of the wiki for additional information.
        Common values:
            1: Y- limit reached
            2: Y+ limit reached
            4: X- limit reached
            8: X+ limit reached
            16: Reset operation
        Returns int latches value.
        """
        self.send_cmd('L')
        resp = self.wait_for_ack()
        # Clean output.
        resp = resp[:-1].strip()
        _, value = resp.split(',')
        return int(value)

    def reset(self):
        """
        Reset the connection and zero the board.
        """
        self.cnxn.flush()
        self.send_cmd('!')  # Reset command.
        self.wait_for_ack()
        l = self.report_latches()
        assert l & 16

        # Zero the valve.
        self.send_cmd('X')  # TODO:See issue 12.
        self.goto(-(self.width + 1000))
        self.wait_for_idle()
        l = self.report_latches()
        assert l & 4  # TODO:See issue 12.
        self.set_pos(-100)
        self.goto(0)
        self.wait_for_idle()

    def send_cmd(self, cmd):
        """
        Write the specified command to the BS1010.
        cmd: String command to write the to the device.
        """
        self._write(cmd)

    def set_runspeed(self, speed: int = 800):
        """
        Set the valve speed in pulses/second/second.
        speed: Int speed value. Defaults to 8000, stop is 80, maxes at 57600.
        """
        self.send_cmd(str(speed) + 'R')
        self.wait_for_ack()

class ThreeWayValve(BS1010):
    """
    Interface for a Three-Way valve controlled by a BS1010, provided by Brechtel.
    See the "Hardware Overview" section of the wiki for information on the BS1010
    and this extension: https://github.com/airpartners/logger/wiki/hardware-overview.
    """
    # The set of named positions and corresponding values.
    positions = {
        'a_open': 0,
        'b_open': 2000,
        'both': 1000,
    }
    # The valve's default speed in pulses/second/second.
    speed = 3200

    def reset(self):
        """
        Reset and zero the valve. Set the speed to the ThreeWayValve default.
        """
        super().reset()
        self.set_runspeed(self.speed)

    def goto_pos(self, pos: str):
        """
        Move to a named position from self.positions.
        """
        self.goto(self.positions[pos])

    def open_a(self):
        """
        Move to position a, as specified in the self.positions.
        """
        self.goto_pos('a_open')

    def open_b(self):
        """
        Move to position b, as specified in the self.positions.
        """
        self.goto_pos('b_open')
