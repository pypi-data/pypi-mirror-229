# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
import micropython_mc3479.mc3479 as MC3479

i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
mc3479 = MC3479.MC3479(i2c)

while True:
    for lpf in MC3479.lpf_values:
        print("Current Low Pass Filter Setting: ", mc3479.lpf_setting)
        for _ in range(10):
            accx, accy, accz = mc3479.acceleration
            print("x:{:.2f}m/s^2, y:{:.2f}m/s^2, z{:.2f}m.s^2".format(accx, accy, accz))
            time.sleep(0.5)
        mc3479.lpf_setting = lpf
