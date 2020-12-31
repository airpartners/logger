# Run this script before running any of the testing and debugging programs.

# On a new device, double check that these ports are stil correct. To do that,
# run the command 'ls /dev/serial/by-id' with each device plugged in individually
# and modify the MCPC and valve port names as required.

# The serial port (by id) associated with the particle counter.
export MCPC_PORT=/dev/serial/by-id/usb-FTDI_UT232R_FT0A3TYQ-if00-port0
# The serial port (by id) associated with the 3-way valve.
export VALVE_PORT=/dev/serial/by-id/usb-FTDI_UT232R_FT2H54CR-if00-port0
# The file to log data from the CPC to.
export SAVE_FILE=/mnt/data/data.csv
# Time to spend on each valve, in seconds.
export VALVE_PERIOD=300
