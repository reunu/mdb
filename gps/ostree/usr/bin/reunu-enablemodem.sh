#!/bin/sh
/usr/bin/gpioset --mode=time --usec=500 gpiochip3 14=1
/bin/sleep 60
python3 /usr/bin/reunu-enablegps.py
