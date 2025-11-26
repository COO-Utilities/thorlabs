#! @KPYTHON3@
""" Thorlabs FW102C controller class """

from errno import ETIMEDOUT, EISCONN
import socket
import threading
import time
from typing import Union

from hardware_device_base import HardwareMotionBase

class FilterWheelController(HardwareMotionBase):
    """ Handle all correspondence with the serial interface of the
        Thorlabs FW102C filter wheel.
    """
    host = ''
    port = 0

    initialized = False
    revision = None

    def __init__(self, log: bool = True, logfile: str = __name__.rsplit(".", 1)[-1]):

        self.lock = threading.Lock()
        self.socket = None

        self.limits = {}

        #initialize Logging through Harware Base Class
        super().__init__(log=log,logfile=logfile)

    def disconnect(self):
        """ Disconnect controller. """

        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None
            if self.logger:
                self.logger.debug("Disconnected controller")
            self._set_connected (False)

        except OSError as e:
            if self.logger:
                self.logger.error("Disconnection error: %s", e.strerror)
            self._set_connected(False)
            self.socket = None


    def connect(self, host, port): # pylint: disable=W0221
        """ Connect to controller. """
        if self.validate_connection_params((host, port)):
            self.host = host
            self.port = port
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((host, port))
                self.report_info(f"Connected to {host}:{port}")
                self._set_connected(True)

            except OSError as e:
                if e.errno == EISCONN:
                    self.report_info("Already connected")
                    self._set_connected(True)
                else:
                    self.report_error(f"Connection error: {e.strerror}")
                    self._set_connected(False)
            # clear socket
            if self.is_connected():
                self._clear_socket()

    def _clear_socket(self):
        """ Clear socket buffer. """
        if self.socket is not None:
            self.socket.setblocking(False)
            while True:
                try:
                    _ = self.socket.recv(1024)
                except BlockingIOError:
                    break
            self.socket.setblocking(True)

    def initialize(self):
        """ Initialize the filter wheel. """

        save = False

        # Give it an initial dummy command to flush out the buffer.
        self._send_command('*idn?')

        self.revision = self._send_command('*idn?')

        # Turn off the position sensors when the wheel is
        # idle to mitigate stray light.

        sensors = self._send_command('sensors?')

        if sensors != '0':
            self._send_command('sensors=0')
            save = True

        # Make sure the wheel is set to move at "high" speed,
        # which takes ~3 seconds to rotate 180 degrees.

        speed = self._send_command('speed?')

        if speed != '1':
            self._send_command('speed=1')
            save = True

        # Make sure the external trigger is in 'output' mode.

        trigger = self._send_command('trig?')

        if trigger != '1':
            self._send_command('trig=1')
            save = True

        if save:
            self._send_command('save')

        limits = self.get_limits()
        for key, value in limits.items():
            self.limits[key] = value

        self.initialized = True


    def _send_command(self, command: str) -> Union[str, None]: # pylint: disable=W0221
        """ Wrapper to issue_command(), ensuring the command lock is
            released if an exception occurs.

        :param command: String, command to issue.

        """

        with self.lock:
            try:
                result = self._issue_command(command)
                if '?' in command and result is None:
                    self.report_error(f"Failed to get response from command: {command}")
            except Exception as e:
                self.report_error(f"Error sending command: {command}")
                raise IOError(f"Failed to issue command: {command}") from e
            self.logger.debug("Command sent to filter wheel")

        return result

    def _issue_command(self, command) -> Union[str, None]:
        """ Wrapper to send/receive with error checking and retries.

        :param command: String, command to issue.

        """
        # pylint: disable=too-many-branches, too-many-statements
        if not self.is_connected():
            self.report_info('connecting')
            self.connect(self.host, self.port)

        retries = 3
        reply = ''
        send_command = f"{command}\r".encode('utf-8')

        while retries > 0:
            self.logger.debug("sending command %s", send_command)
            try:
                self.socket.send(send_command)

            except socket.error:
                self.report_error(
                    f"Failed to send command, re-opening socket, {retries} retries "
                    f"remaining")
                self.disconnect()
                try:
                    self.connect(self.host, self.port)
                except OSError:
                    self.report_error('Could not reconnect to controller, aborting')
                    return None
                retries -= 1
                continue

            # Wait for a reply.
            delimiter = b'>'

            if 'pos=' in command:
                # The next response will wait
                # until the filter wheel is
                # actually in position.
                timeout = 5
            else:
                timeout = 1

            start = time.time()
            time.sleep(0.1)
            reply = self.socket.recv(1024)
            while delimiter not in reply and time.time() - start < timeout:
                try:
                    reply += self.socket.recv(1024)
                    self.logger.debug("reply: %s", reply)
                except OSError as e:
                    if e.errno == ETIMEDOUT:
                        reply = ''
                time.sleep(0.1)

            if reply == '':
                # Don't log here, because it happens a lot when the controller
                # is unresponsive. Just try again.
                retries -= 1
                continue
            break

        if isinstance(reply, str):
            reply = reply.strip()
        else:
            reply = reply.decode('utf-8')

        if retries <= 0:
            self.report_error("Failed to send command.")
            raise RuntimeError('unable to successfully issue command: ' + repr(command))

        # For a command with a reply, the response always looks like:
        #
        #    command\rreply\r>
        #
        # For commands that do not have a reply, the response is:
        #
        #    command\r>

        if command[-1] == '?':
            expected = 3
        else:
            expected = 2

        chunks = reply.split('\r')

        if len(chunks) != expected:
            raise ValueError(f"unexpected number of fields in response: {repr(reply)}")

        if expected == 3:
            return chunks[1]

        return None

    def _set_pcount(self, pcount:int) -> bool:
        """ Set the pcount of the filter wheel.
        :param pcount: Int, pcount to set.
        """
        self._send_command(f'pcount={pcount}')
        time.sleep(0.1)
        reply = self._send_command("pcount?")
        if reply != pcount:
            self.report_error(f"pcount not set: {pcount}")
            return False
        self.report_info(f"pcount set: {pcount}")
        return True

    def get_pos(self) -> Union[int, None]:  # pylint: disable=W0221
        """ Get the current position from the controller."""
        pos = self._send_command('pos?')
        if pos is not None:
            return int(pos)
        self.report_error("Failed to get position.")
        return None

    def set_pos(self, target: int) -> bool:  # pylint: disable=W0221
        """ Move the filter wheel to the target position.

        :param target: Int, target position to move.

        """
        if not self.initialized:
            self.initialize()

        target = int(target)
        if self.limits["1"][0] <= target <= self.limits["1"][1]:
            command = f"pos={target:d}"

            response = self._send_command(command)

            if response is not None:
                raise RuntimeError(f"error response to command: {response}")

            current = int(self.get_pos())

            if current != target:
                self.report_error(
                    f"wound up at position {current:d} instead of commanded {target:d}")
                return False
            return True

        self.report_error(f"target position out of range: {target:d}")
        return False

    #Required abstract baseclass methods
    def _read_reply(self):
        """Receive a reply from the device.
        :return: The reply or None if no reply was received."""
        #Not needed for this device
        return NotImplemented

    # abstract Motion methods below
    def close_loop(self):
        """Close the loop for the hardware motion device."""
        return True

    def is_loop_closed(self):
        """Check if the hardware motion device is closed loop."""
        return True

    def home(self):
        """Home the hardware motion device."""
        return True

    def is_homed(self):
        """Check if the hardware motion device is homed."""
        return True

    def get_limits(self) -> Union[dict, None]:
        """Get the limits of the hardware motion device."""
        reply = self._send_command('pcount?')
        if reply is not None:
            return {"1": (1, int(reply))}
        self.report_error("Failed to get limits.")
        return None

# end of class Controller
