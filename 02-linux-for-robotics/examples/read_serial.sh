#!/bin/bash
# Read from /dev/drone_radio
stty -F /dev/drone_radio 57600 raw -echo
cat /dev/drone_radio
