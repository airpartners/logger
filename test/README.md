# Test
This folder contains test code associated with developing features for and
debugging the components of the sensor box. 

The scripts assume that the raspberry pi has environment variables set for the
switching period, valve serial port, and MCPC serial port. To set those values,
run the following command in terminal:
```
source setup_testing.sh
```
To change any of the values of the environment variables, either change the
value already hardcoded in `setup_testing` or overwrite the value with the
following command in terminal:
```
export VARIABLE_TO_OVERRIDE="new_value"
```
The [common](https://github.com/airpartners/logger/tree/master/test/common.py)
file contains some functions for getting envrionment variables.

The tests in this folder leverage this approach for connecting to peripheral 
devices (rather than expecting an input argument) by default. If
this isn't the case in a particular test, add a comment about why that is the
case and what the procedure is, or change the documentation to reflect the 
change in team practice.
