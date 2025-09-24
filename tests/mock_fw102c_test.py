"""Test suite for the FilterWheel class in hispec.util module."""
import unittest
from unittest.mock import patch, MagicMock
from thorlabs.fw102c import FilterWheelController

class TestFilterWheelController(unittest.TestCase):
    """Unit tests for the FilterWheelController class."""

    @patch("socket.socket")
    def setUp(self, mock_serial): # pylint: disable=arguments-differ
        """Set up the test case with a mocked socket connection."""
        self.mock_socket = MagicMock()
        mock_socket_obj.return_value = self.mock_socket
        self.mock_socket.read.return_value = b""
        self.controller = FilterWheelController(log=False)
        self.controller.set_connection(ip="123.456.789.101", port=1234)
        self.controller.connected = True

    def test_send_command(self):
        """Test sending a command to the filter wheel."""
        self.controller.command("TEST") # pylint: disable=protected-access
        self.mock_socket.write.assert_called_with(b"TEST")

    def test_get_position(self):
        """Test getting the position of the filter wheel."""
        with patch.object(self.controller, "command") as mock_command:
            self.controller.get_posiion()
            mock_command.assert_called_once_with("pos?")

    def test_set_position(self):
        """Test setting the position of the filter wheel."""
        with patch.object(self.controller, "move") as mock_move:
            self.controller.initialized = True
            self.controller.move(target = 10)
            mock_move.assert_called_once_with("pos=10")



if __name__ == "__main__":
    unittest.main()