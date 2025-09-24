"""Test suite for the PPC102 Coms class in hispec.util module."""
import unittest
from unittest.mock import patch, MagicMock
# pylint: disable=import-error,no-name-in-module
from thorlabs.ppc102 import PPC102_Coms


class TestPPC102_Coms(unittest.TestCase):
    """Unit tests for the SunpowerCryocooler class."""

    @patch("socket.socket")
    def setUp(self, mock_socket_obj): # pylint: disable=arguments-differ
        """Set up the test case with a mocked socket connection."""
        self.mock_socket = MagicMock()
        mock_socket_obj.return_value = self.mock_socket
        self.mock_socket.read.return_value = b""
        self.controller = PPC102_Coms(IP="123.456.789.101", port=1234, log=False)
        self.controller.sock = self.mock_socket
        self.controller.get_loop()


    def test_send_command(self):
        """Test sending _get_infocommand to the controller."""
        self.controller._get_info() # pylint: disable=protected-access
        self.mock_socket.write.assert_called_with(bytes([0x05, 0x00, 0x00, 0x00, 0x11, 0x01]))

    def test_get_loop(self):
        """Testing sending the correct bytes to get the loop status from the gimbal."""
        with patch.object(self.controller, "get_loop") as mock_get_loop:
            self.controller.get_loop(channel = 1)
            mock_get_loop.assert_called_once_with(bytes([0x41, 0x06, 0x01, 0x00, 0x21, 0x01]))
        
    def test_get_status_update(self):
        """Test setting the status from the Gimbal."""
        with patch.object(self.controller, "get_status_update") as mock_status:
            self.controller.get_status_update(channel = 1)
            dest = 0x20 + 1
            mock_status.assert_called_once_with(bytes([0x60, 0x06, 0x01, 0x00, dest, 0x01]))

    def test_get_position(self):
        """Test getting the position from the Gimbal."""
        #make get_loop and get_enable return the correct responses using MagicMock
        self.controller.get_loop = MagicMock(return_value=2)
        self.controller.get_enable = MagicMock(return_value=1)
        with patch.object(self.controller, "position") as mock_gposition:
            self.controller.get_posiion(channel = 1)
            dest = 0x20 + 1
            mock_gposition.assert_called_once_with(bytes([0x47, 0x06, 0x01, 0x00, dest, 0x01]))
        
    def test_set_position(self):
        """Test setting the position from the Gimbal."""
        #make get_loop and get_enable return the correct responses using MagicMock
        self.controller.get_loop = MagicMock(return_value=2)
        self.controller.get_enable = MagicMock(return_value=1)
        with patch.object(self.controller, "set_position") as mock_setpos:
            self.controller.set_position(channel = 1, position = 5.0)
            dest = (0x20 + channel) | 0x80 
            converted_pos = int(round((5.0 + 10)/20*32767))
            pos_bytes = converted_pos.to_bytes(4, byteorder='little', signed=False)
            mock_setpos.assert_called_once_with(bytes([0x47, 0x10, 0x05, 0x00, dest, 0x04]) + pos_bytes)



if __name__ == "__main__":
    unittest.main()