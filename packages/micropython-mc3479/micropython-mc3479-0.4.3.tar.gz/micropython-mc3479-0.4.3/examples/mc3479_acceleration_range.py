# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

from machine import Pin, I2C
import micropython_mc3479.mc3479 as MC3479

i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
mc3479 = MC3479.MC3479(i2c)

print("Current Acceleration Range")
print("Acceleration Range", mc3479.acceleration_range)
print("Changing Acceleration range to 8G")
mc3479.acceleration_range = MC3479.ACCEL_RANGE_8G
print("Acceleration Range", mc3479.acceleration_range)
print("Changing Acceleration Range to 4G")
mc3479.acceleration_range = MC3479.ACCEL_RANGE_4G
print("Acceleration Range", mc3479.acceleration_range)
print("Changing Acceleration Range to 16G")
mc3479.acceleration_range = MC3479.ACCEL_RANGE_16G
print("Acceleration Range", mc3479.acceleration_range)
