#!/bin/sh
# 0: Hauptlicht
# 1: Ring vorne
# 2: Bremslicht
# 3: Blinker VL
# 4: Blinker HR
# 5: Kennzeichenbeleuchtung
# 6: Blinker HL
# 7: Blinker VR

/home/root/ioctl /dev/pwm_led$1 0x00007545 -v $2 > /dev/null
