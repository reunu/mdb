#!/bin/sh
/usr/bin/gpioset --mode=time --usec=500 gpiochip3 14=1
/bin/sleep 60
echo 1-1 > /sys/bus/usb/drivers/usb/unbind
/bin/sleep 15
echo 1-1 > /sys/bus/usb/drivers/usb/bind
/bin/sleep 15
python3 /usr/bin/reunu-enablegps.py
