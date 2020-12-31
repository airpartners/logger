# Test
This folder contains test code associated with the development features for and
debugging of the components of the sensor box. 

The scripts assume that the raspberry pi has environment variables set for the
switching period, valve serial port, and MCPC serial port. To set those values,
run the following command:
```
source setup_debug.sh
```
To change any of the values of the environment variables, either change the
value already hardcoded in `setup_debug` or overwrite the value with the
following command.
```
export VARIABLE_TO_OVERRIDE="new_value"
```
The [common](https://github.com/airpartners/logger/tree/master/test/common.py)
file contains some functions for getting envrionment variables.
By default, all of the tests in this folder should leverage this approach for
connecting to peripheral devices (rather than expecting an input argument). If
this isn't the case in a particular test, add a comment about why that is the
case.