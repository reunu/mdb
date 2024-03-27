#!/bin/sh
# 0: Hauptlicht
# 1: Ring vorne
# 2: Bremslicht
# 3: Blinker VL
# 4: Blinker HR
# 5: Kennzeichenbeleuchtung
# 6: Blinker HL
# 7: Blinker VR

/home/root/ioctl /dev/pwm_led$1 0x00007541 -v 0 > /dev/null
sleep 0.1
cat /usr/share/led-curves/fades/$2 > /dev/pwm_led$1
# /home/root/ioctl /dev/pwm_led$1 0x00007542 -v 0 > /dev/null
# printf "\x00\x00\x00\x00\x01\x00\x00\x00" > /dev/pwm_led$1
/home/root/ioctl /dev/pwm_led$1 0x00007545 -v 0 > /dev/null
# /home/root/ioctl /dev/pwm_led$1 0x00007543 -v 0 > /dev/null