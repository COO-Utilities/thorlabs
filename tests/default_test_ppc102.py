#################
#Default Communication test
#################

import pytest
import sys
import os
import unittest
import time
from thorlabs.ppc102 import PPC102_Coms

##########################
## CONFIG
## connection and Disconnection in all test
##########################

class Default_Test(unittest.TestCase):

    #Instances for Test management
    def setUp(self):
        self.dev = None
        self.success = True
        self.IP = ''
        self.port = 10013
        self.log = False
        self.error_tolerance = 0.1


    ##########################
    ## Negative test: failed connect
    ##########################
    def failed_connect_test(self):
        # Use an unreachable IP (TEST-NET-1 range, reserved for docs/testing)
        bad_ip = "192.1.2.123"
        bad_port = 65535  # usually blocked/unusable

        dev = PPC102_Coms(IP=bad_ip, port=bad_port, log=self.log)

        success = dev.open()
        self.assertFalse(dev.sock, "Expected connection failure with invalid IP/port")
        dev.close()

    
    ##########################
    ## Comms/Info Grab
    ##########################
    def comms_test(self):
        self.dev = PPC102_Coms(IP=self.IP, port = self.port,log = self.log)
        assert self.dev.open() #With valid IP/port a connection will return true
        time.sleep(.25)
        self.dev.close()
        time.sleep(.25)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Default_Test)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
