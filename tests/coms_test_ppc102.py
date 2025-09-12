#################
#Outline Robust and Communication Tests
#################

import pytest
import sys
import os
import unittest
import time 

##########################
## CONFIG
## connection and Disconnection in all test
##########################

class Comms_Test(unittest.TestCase):

    #Instances for Test management
    def setUp(self):
        self.dev = None
        self.success = True
        self.IP = ''
        self.port = 10013
        self.log = False
        self.error_tolerance = 0.1

    ##########################
    ## Servos / Loops [ Not really applicable]
    ##########################
    def test_loop(self):
        self.dev = #Controller/Library for the device
        time.sleep(.2)
        self.dev.open()
        time.sleep(.25)
        for ch in [1,2]:#Check for channels that are applicable
            #Close Loop assert Loop states

            #Open Loops and assert the states

        #Exception Handling
            except Exception as e:
                self.fail(f"Failed to test loop: {e}")
                self.dev.close()
                self.success = False
            #Close connection
        self.dev.close()
        time.sleep(.25)


    ##########################
    ## Limit Check
    ##########################
    def test_limit(self):
        self.dev = #Controller/Library for the device
        self.dev.open()
        time.sleep(.25)
        for ch in [1,2]:  # Check for channels that are applicable
            # Check limit states and save to variable
            
            # Set limit states and assert

            # set limits back to default

        #Exception Handling
            except Exception as e:
                self.fail(f"Failed to test loop: {e}")
                self.dev.close()
                self.success = False
            #Close connection
        self.dev.close()
        time.sleep(.25)

    ##########################
    ## Position Query and Movement
    ##########################
    def test_position_query(self):
        self.dev = #Controller/Library for the device
        self.dev.open()
        time.sleep(.25)
        for ch in [1,2]:  # Check for channels that are applicable
            # Close loops and assert
            
            # Get position and assert

            #open loops and assert

        #Exception Handling
            except Exception as e:
                self.fail(f"Failed to test loop: {e}")
                self.dev.close()
                self.success = False
            #Close connection
        self.dev.close()
        time.sleep(.25)

    ##########################
    ## Comms/Info Grab
    ##########################
    def info_grab(self):
        self.dev = #Controller/Library for the device
        self.dev.open()
        time.sleep(.25)
        # Get device info and assert
        # Get firmware version and assert
        # Get serial number and assert
        # Get model number and assert
        self.dev.close()
        time.sleep(.25)


    ##########################
    ## Status Communication
    ##########################
    def status_communication(self):
        self.dev = #Controller/Library for the device
        self.dev.open()
        time.sleep(.25)
        # Get status and assert
        # Get error codes and assert
        self.dev.close()
        time.sleep(.25)


if __name__ == '__main__':
    #Determine test, Robust or Comms
    if 'robust' in sys.argv:
        test_class = Robust_Test
    elif 'comms' in sys.argv:
        test_class = Comms_Test
    else:
        raise ValueError("Please specify 'robust' or 'comms' in the command line arguments.")

    #load the test into a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_class)

    #run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    #Using exit return code based on test results
    sys.exit(0)
