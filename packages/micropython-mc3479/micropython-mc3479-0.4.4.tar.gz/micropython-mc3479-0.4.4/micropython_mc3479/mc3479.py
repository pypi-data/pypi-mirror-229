# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`mc3479`
================================================================================

MC3479 Accelerometer MicroPython Driver


* Author: Jose D. Montoya


"""

from micropython import const
from micropython_mc3479.i2c_helpers import CBits, RegisterStruct

try:
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.4.4"
__repo__ = "https://github.com/jposada202020/MicroPython_MC3479.git"

_REG_WHOAMI = const(0x98)
_SENSOR_STATUS_REG = const(0x05)
_MODE_REG = const(0x07)
_ACC_RANGE = const(0x20)
_ACC_DATA_RATE = const(0x08)

# Acceleration Data
ACC_X_LSB = const(0x0D)
ACC_X_MSB = const(0x0E)
ACC_Y_LSB = const(0x0F)
ACC_Y_MSB = const(0x10)
ACC_Z_LSB = const(0x11)
ACC_Z_MSB = const(0x12)

# Sensor Power
STANDBY = const(0)
NORMAL = const(1)

# Acceleration Range
ACCEL_RANGE_2G = const(0b000)
ACCEL_RANGE_4G = const(0b001)
ACCEL_RANGE_8G = const(0b010)
ACCEL_RANGE_16G = const(0b011)
ACCEL_RANGE_12G = const(0b100)
accel_range_values = (
    ACCEL_RANGE_2G,
    ACCEL_RANGE_4G,
    ACCEL_RANGE_8G,
    ACCEL_RANGE_16G,
    ACCEL_RANGE_12G,
)

LPF_ENABLE = const(1)
LPF_DISABLE = const(0)

BANDWIDTH_1 = const(0b001)
BANDWIDTH_2 = const(0b010)
BANDWIDTH_3 = const(0b011)
BANDWIDTH_5 = const(0b101)
lpf_setting_values = (BANDWIDTH_1, BANDWIDTH_2, BANDWIDTH_3, BANDWIDTH_5)

# Acceleration Output Rate HZ
BANDWIDTH_25 = const(0x10)  # 25 Hz
BANDWIDTH_50 = const(0x11)  # 50 Hz
BANDWIDTH_62_5 = const(0x12)  # 62.5 Hz
BANDWIDTH_100 = const(0x13)  # 100 Hz
BANDWIDTH_125 = const(0x14)  # 125 Hz
BANDWIDTH_250 = const(0x15)  # 250 Hz
BANDWIDTH_500 = const(0x16)  # 500 Hz
BANDWIDTH_1000 = const(0x17)  # 1000 Hz
acceleration_output_data_rate_values = (
    BANDWIDTH_25,
    BANDWIDTH_50,
    BANDWIDTH_62_5,
    BANDWIDTH_100,
    BANDWIDTH_125,
    BANDWIDTH_250,
    BANDWIDTH_500,
    BANDWIDTH_1000,
)


class MC3479:
    """Driver for the MC3479 Sensor connected over I2C.

    :param ~machine.I2C i2c: The I2C bus the MC3479 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x4C`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`micropython_mc3479.MC3479` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        import micropython_mc3479 as MC3479

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
        mc3479 = MC3479.MC3479(i2c)

    Now you have access to the attributes

    .. code-block:: python

        accx, accy, accz = mc3479.acceleration

    """

    _device_id = RegisterStruct(_REG_WHOAMI, "B")
    _status = RegisterStruct(_SENSOR_STATUS_REG, "B")
    _mode_reg = RegisterStruct(_MODE_REG, "B")
    _range_scale_control = RegisterStruct(_ACC_RANGE, "B")
    _data_rate = RegisterStruct(_ACC_DATA_RATE, "B")

    # Acceleration Data
    _acc_data_x_msb = RegisterStruct(ACC_X_MSB, "B")
    _acc_data_x_lsb = RegisterStruct(ACC_X_LSB, "B")
    _acc_data_y_msb = RegisterStruct(ACC_Y_MSB, "B")
    _acc_data_y_lsb = RegisterStruct(ACC_Y_LSB, "B")
    _acc_data_z_msb = RegisterStruct(ACC_Z_MSB, "B")
    _acc_data_z_lsb = RegisterStruct(ACC_Z_LSB, "B")

    _mode = CBits(2, _MODE_REG, 0)

    # Acceleration Range Conf (0x20)
    _acc_range = CBits(3, _ACC_RANGE, 4)
    _acc_lpf_en = CBits(1, _ACC_RANGE, 3)
    _acc_lpf_setting = CBits(3, _ACC_RANGE, 0)

    acceleration_scale = {
        "ACCEL_RANGE_2G": 16384,
        "ACCEL_RANGE_4G": 8192,
        "ACCEL_RANGE_8G": 4096,
        "ACCEL_RANGE_16G": 2048,
        "ACCEL_RANGE_12G": 2730,
    }

    def __init__(self, i2c, address: int = 0x4C) -> None:
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xA4:
            raise RuntimeError("Failed to find the MC3479 sensor")

        self._mode = NORMAL

    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        The device has the ability to read all sampled readings
        in a continuous sampling fashion. The device always updates
        the XOUT, YOUT, and ZOUT registers at the chosen output data rate

        X, Y, and Z-axis accelerometer measurements are in 16-bit, signed
        2's complement format. Register addresses 0x0D to 0x12 hold the
        latest sampled data from the X, Y, and Z accelerometers.
        """

        factor = self.acceleration_scale[self.acceleration_range]

        x = (self._acc_data_x_msb * 256 + self._acc_data_x_lsb) / factor
        y = (self._acc_data_y_msb * 256 + self._acc_data_y_lsb) / factor
        z = (self._acc_data_z_msb * 256 + self._acc_data_z_lsb) / factor

        return x, y, z

    @property
    def sensor_mode(self) -> str:
        """
        Standby
        ********

        * Lowest power consumption
        * Internal clocking is halted
        * No motion detection, sampling, or calibration
        * The I2C/SPI bus can read and write to registers (resolution, range, thresholds and other
          settings can be changed)
        * Reset not allowed
        * Default state after a power-up


        Normal
        *******

        * Highest power consumption
        * Internal clocking is enabled
        * Continuous motion detection and sampling; automatic calibration is available
        * The I2C/SPI bus can only write to the mode register and read all other registers
        * Reset allowed


        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`MC3479.STANDBY`             | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.NORMAL`              | :py:const:`1`           |
        +----------------------------------------+-------------------------+


        """
        values = ("STANDBY", "NORMAL")
        return values[self._mode]

    @sensor_mode.setter
    def sensor_mode(self, value: int) -> None:
        if value not in (STANDBY, NORMAL):
            raise ValueError("Invalid Sensor Mode")
        self._mode = value

    @property
    def acceleration_range(self) -> str:
        """
        The range and scale control register sets the resolution, range,
        and filtering options for the accelerometer. All values are in
        sign-extended 2's complement format. Values are reported in
        registers 0x0D - 0x12 (the hardware formats the output)

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`MC3479.ACCEL_RANGE_2G`      | :py:const:`0b000`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_4G`      | :py:const:`0b001`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_8G`      | :py:const:`0b010`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_16G`     | :py:const:`0b011`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_12G`     | :py:const:`0b100`       |
        +----------------------------------------+-------------------------+

        Example
        ########

        .. code-block:: python

            i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
            mc3479 = MC3479.MC3479(i2c)
            mc3479.acceleration_range = MC3479.ACCEL_RANGE_12G

        """
        values = (
            "ACCEL_RANGE_2G",
            "ACCEL_RANGE_4G",
            "ACCEL_RANGE_8G",
            "ACCEL_RANGE_16G",
            "ACCEL_RANGE_12G",
        )
        return values[self._acc_range]

    @acceleration_range.setter
    def acceleration_range(self, value: int) -> None:
        if value not in accel_range_values:
            raise ValueError("Invalid Acceleration Range")
        self._mode = STANDBY
        self._acc_range = value
        self._mode = NORMAL

    @property
    def lpf_enabled(self) -> str:
        """
        Low Power Filter Enabler

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`MC3479.LPF_ENABLE`          | :py:const:`0b0`         |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.LPF_DISABLE`         | :py:const:`0b1`         |
        +----------------------------------------+-------------------------+

        Example
        ---------------------

        .. code-block:: python

            i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
            mc3479 = MC3479.MC3479(i2c)
            mc3479.lpf_enabled = MC3479.LPF_ENABLE

        """
        values = ("LPF_DISABLE", "LPF_ENABLE")
        return values[self._acc_lpf_en]

    @lpf_enabled.setter
    def lpf_enabled(self, value: int) -> None:
        if value not in (LPF_ENABLE, LPF_DISABLE):
            raise ValueError("Invalid Low Pass Filter Setting")
        self._mode = STANDBY
        self._acc_lpf_en = value
        self._mode = NORMAL

    @property
    def lpf_setting(self) -> str:
        """
        Selects the Bandwidth for the Low Power Filter. Depends on the selection
        of the ODR/IDR

        +--------------------------------+------------------------------------+
        | Mode                           | Value                              |
        +================================+====================================+
        | :py:const:`MC3479.BANDWIDTH_1` | :py:const:`0b001` Fc = IDR / 4.255 |
        +--------------------------------+------------------------------------+
        | :py:const:`MC3479.BANDWIDTH_2` | :py:const:`0b010` Fc = IDR / 6     |
        +--------------------------------+------------------------------------+
        | :py:const:`MC3479.BANDWIDTH_3` | :py:const:`0b011` Fc = IDR / 12    |
        +--------------------------------+------------------------------------+
        | :py:const:`MC3479.BANDWIDTH_5` | :py:const:`0b101` Fc = IDR / 16    |
        +--------------------------------+------------------------------------+

        Example
        ---------------------

        .. code-block:: python

            i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
            mc3479 = MC3479.MC3479(i2c)

            mc3479.lpf_setting = MC3479.BANDWIDTH_5

        """
        values = {
            1: "BANDWIDTH_1",
            2: "BANDWIDTH_2",
            3: "BANDWIDTH_3",
            5: "BANDWIDTH_5",
        }
        return values[self._acc_lpf_setting]

    @lpf_setting.setter
    def lpf_setting(self, value: int) -> None:
        if value not in lpf_setting_values:
            raise ValueError("Invalid Low Pass Filter Setting")
        self._mode = STANDBY
        self._acc_lpf_setting = value
        self._mode = NORMAL

    @property
    def acceleration_output_data_rate(self) -> str:
        """
        Define the output data rate in Hz
        The output data rate is dependent of the power mode setting for the sensor

        +----------------------------------------+---------------------------------+
        | Mode                                   | Value                           |
        +========================================+=================================+
        | :py:const:`MC3479.BANDWIDTH_25`        | :py:const:`0x10` 25 Hz          |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_50`        | :py:const:`0x11` 50 Hz          |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_62_5`      | :py:const:`0x12` 62.5 Hz        |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_100`       | :py:const:`0x13` 100 Hz         |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_125`       | :py:const:`0x14` 125 Hz         |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_250`       | :py:const:`0x15` 250 Hz         |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_500`       | :py:const:`0x16` 500 Hz         |
        +----------------------------------------+---------------------------------+
        | :py:const:`MC3479.BANDWIDTH_1000`      | :py:const:`0x17` 1000 Hz        |
        +----------------------------------------+---------------------------------+

        Example
        ########

        .. code-block:: python

            i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
            mc3479 = MC3479.MC3479(i2c)
            mc3479.acceleration_output_data_rate = MC3479.BANDWIDTH_500

        """
        values = {
            0x10: "BANDWIDTH_25",
            0x11: "BANDWIDTH_50",
            0x12: "BANDWIDTH_62_5",
            0x13: "BANDWIDTH_100",
            0x14: "BANDWIDTH_125",
            0x15: "BANDWIDTH_250",
            0x16: "BANDWIDTH_500",
            0x17: "BANDWIDTH_1000",
        }
        return values[self._data_rate]

    @acceleration_output_data_rate.setter
    def acceleration_output_data_rate(self, value: int) -> None:
        if value not in acceleration_output_data_rate_values:
            raise ValueError("Invalid Output Data Rate")
        self._mode = STANDBY
        self._data_rate = value
        self._mode = NORMAL
