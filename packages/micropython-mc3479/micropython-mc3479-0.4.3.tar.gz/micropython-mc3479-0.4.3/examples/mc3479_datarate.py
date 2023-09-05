# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

from machine import Pin, I2C
import micropython_mc3479.mc3479 as MC3479

i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
mc3479 = MC3479.MC3479(i2c)

print("Current Acceleration data rate", mc3479.acceleration_output_data_rate)
print("Changing Acceleration data rate to 25 Hz")
mc3479.acceleration_output_data_rate = MC3479.BANDWIDTH_25
print("Changed Acceleration data rate", mc3479.acceleration_output_data_rate)
print("Changing Acceleration data rate to 62.5 Hz")
mc3479.acceleration_output_data_rate = MC3479.BANDWIDTH_62_5
print("Changed Acceleration data rate", mc3479.acceleration_output_data_rate)
print("Changing Acceleration data rate to 1000")
mc3479.acceleration_output_data_rate = MC3479.BANDWIDTH_1000
print("Changed Acceleration data rate", mc3479.acceleration_output_data_rate)
