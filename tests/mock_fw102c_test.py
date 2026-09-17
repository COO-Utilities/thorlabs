"""
Unit test
Description: Validate software functions are correctly implemented via mocking
"""

import unittest
from unittest.mock import patch, MagicMock, call
import pytest
from fw102c import FilterWheelController

pytestmark = pytest.mark.unit


class TestFilterWheelController(unittest.TestCase):
    """Unit tests for the FilterWheelController class."""

    @patch("socket.socket")
    def setUp(self, mock_socket_obj): # pylint: disable=arguments-differ
        """Set up the test case with a mocked socket connection."""
        self.mock_socket = MagicMock()
        mock_socket_obj.return_value = self.mock_socket
        self.mock_socket.recv.side_effect = BlockingIOError
        self.controller = FilterWheelController(log=False)
        self.controller.connect("123.456.789.101", 1234)
        self.controller.connected = True

    def test_get_position(self):
        """Test getting the position of the filter wheel."""
        with patch.object(self.controller, "_send_command") as mock_command:
            self.controller.get_pos()
            mock_command.assert_called_once_with("pos?")

    def test_set_position(self):
        """Test setting the position of the filter wheel."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = None
            with patch.object(self.controller, "get_pos") as mock_getpos:
                mock_getpos.return_value = 10
                self.controller.initialized = True
                self.controller.limits = {"1": (1, 12)}
                self.controller.set_pos(target = 10)
                mock_command.assert_called_once_with("pos=10")

    def test_get_light_on(self):
        """Test reading the LED mode when the LED is always on."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = "1"
            assert self.controller.get_light() is True
            mock_command.assert_called_once_with("sensors?")

    def test_get_light_off(self):
        """Test reading the LED mode when the LED sleeps while idle."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = "0"
            assert self.controller.get_light() is False

    def test_get_light_bad_reply(self):
        """Test that an unexpected LED mode reply returns None."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = "x"
            assert self.controller.get_light() is None

    def test_set_light_on_saves_mode(self):
        """Test that turning the LED on is followed by a save."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = None
            with patch.object(self.controller, "get_light") as mock_getlight:
                mock_getlight.return_value = True
                assert self.controller.set_light(True) is True
                assert mock_command.call_args_list == [call("sensors=1"), call("save")]

    def test_set_light_off_saves_mode(self):
        """Test that letting the LED sleep while idle is followed by a save."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = None
            with patch.object(self.controller, "get_light") as mock_getlight:
                mock_getlight.return_value = False
                assert self.controller.set_light(False) is True
                assert mock_command.call_args_list == [call("sensors=0"), call("save")]

    def test_set_light_readback_mismatch(self):
        """Test that a LED mode that does not stick returns False."""
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.return_value = None
            with patch.object(self.controller, "get_light") as mock_getlight:
                mock_getlight.return_value = False
                assert self.controller.set_light(True) is False

    def test_initialize_keeps_sensor_mode(self):
        """Test that initialize leaves the saved LED mode alone."""
        replies = {"*idn?": "rev", "sensors?": "0", "speed?": "1",
                   "trig?": "1", "pcount?": "6"}
        with patch.object(self.controller, "_send_command") as mock_command:
            mock_command.side_effect = replies.get
            self.controller.initialize()
            sent = [args[0] for args, _ in mock_command.call_args_list]
            assert "sensors=0" not in sent
            assert "save" not in sent


if __name__ == "__main__":
    unittest.main()
