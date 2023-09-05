# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

import time
from machine import Pin, I2C
import micropython_mc3479.mc3479 as MC3479

i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
mc3479 = MC3479.MC3479(i2c)

while True:
    accx, accy, accz = mc3479.acceleration
    print("Acceleration X: ", accx)
    print("Acceleration Y: ", accy)
    print("Acceleration Z: ", accz)
    time.sleep(0.5)
