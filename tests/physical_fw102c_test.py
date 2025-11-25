"""
Functionality test
Description: Test connection, disconnection, confirming communication with stage,
               inicialization(or something similar) and movement/position query
               tests are successful and correct
"""
import sys
import unittest
import time
import pytest
from fw102c import FilterWheelController

pytestmark = pytest.mark.functional


##########################
## CONFIG
## connection and Disconnection in all test
##########################
class PhysicalTest(unittest.TestCase):
    """Instances for Test management"""
    def setUp(self):
        self.dev = FilterWheelController()
        self.success = True
        self.host = '192.168.29.100'
        self.port = 10010
        self.log = False
        self.error_tolerance = 0.1

    ##########################
    ## Test Connection
    ##########################
    def test_connection(self):
        """Connection test"""
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

    def initialize(self):
        """Initialization test"""
        self.dev = FilterWheelController(log = self.log)
        self.dev.connect(self.host, self.port)
        time.sleep(.25)
        self.dev.initialize()
        time.sleep(.25)
        assert self.dev.initialized
        assert self.dev.revision is not None
        self.dev.disconnect()
        time.sleep(.25)

    ##########################
    ## Position Query and Movement
    ##########################
    def test_position_query_and_movement(self):
        """Position query and movement test"""
        self.dev = FilterWheelController(log = self.log)
        self.dev.connect(self.host, self.port)
        time.sleep(.25)
        self.dev.initialize()
        # Set position and assert
        self.dev.set_pos(1)
        time.sleep(.25)
        ret = self.dev.get_pos()
        assert ret == 1
        self.dev.set_pos(2)
        time.sleep(.25)
        ret = self.dev.get_pos()
        assert ret == 2
        self.dev.set_pos(5)
        time.sleep(.25)
        ret = self.dev.get_pos()
        assert ret == 5
        self.dev.set_pos(1)
        time.sleep(.25)
        ret = self.dev.get_pos()
        assert ret == 1
        #Close connection
        self.dev.disconnect()
        time.sleep(.25)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(PhysicalTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
