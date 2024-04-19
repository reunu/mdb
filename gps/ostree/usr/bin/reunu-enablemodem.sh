#!/bin/sh
/usr/bin/gpioset --mode=time --usec=500 gpiochip3 14=1
python3 reunu-enablegps.py
