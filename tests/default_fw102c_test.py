"""
Default Communication test
Description: Test connection, disconnection and confirming communication with stage
"""
import sys
import unittest
import time
import pytest
from fw102c import FilterWheelController

pytestmark = pytest.mark.default

##########################
## CONFIG
## connection and Disconnection in all test
##########################

class DefaultTest(unittest.TestCase):

    """Instances for Test management"""
    def setUp(self):
        self.dev = FilterWheelController()
        self.success = True
        self.host = '192.168.29.100'
        self.port = 10010
        self.log = False
        self.error_tolerance = 0.1

    def test_connection(self):
        """Test connection mode"""
        time.sleep(.2)
        # Open connection
        self.dev = FilterWheelController(log = self.log)
        assert self.dev.status is None
        self.dev.connect(self.host, self.port)
        time.sleep(.25)
        assert self.dev.connected
        # assert self.dev.status == 'ready'
        self.dev.disconnect()
        time.sleep(.25)
        assert not self.dev.connected
        # assert self.dev.status == 'disconnected'
        time.sleep(.25)

    def failed_connect_test(self):
        """Negative test: failed connect"""
        # Use an unreachable host (TEST-NET-1 range, reserved for docs/testing)
        bad_ip = "192.1.2.123"
        bad_port = 65535  # usually blocked/unusable

        self.dev = FilterWheelController(log=self.log)
        self.dev.connect(bad_ip, bad_port)
        time.sleep(.25)
        assert self.dev.connected is False, "Expected not connected state with invalid host/port"
        self.assertFalse(self.dev.connected, "Expected connection failure with invalid host/port")
        self.dev.disconnect()
        time.sleep(.25)

    def initialize(self):
        """Negative test: initialize"""
        self.dev = FilterWheelController(log = self.log)
        self.dev.connect(self.host, self.port)
        time.sleep(.25)
        self.dev.initialize()
        time.sleep(.25)
        assert self.dev.initialized
        assert self.dev.revision is not None
        self.dev.disconnect()
        time.sleep(.25)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(DefaultTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
