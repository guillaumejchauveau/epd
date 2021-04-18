import RPi.GPIO
import spidev
import time
import EPDExceptions


class DisplayInterface:
    def __init__(self, commands: dict):
        """
        The display interface is the hardware interface used to communicated with the EPD device.

        :param commands: The commands recognized by the device.
        :type commands: dict
        """
        self.__commands = commands

        # Wait times (s).
        self.WT_PIN_TOGGLE = 0.2
        self.WT_STATE_LOOKUP = 0.1

        # GPIO pins.
        self.RST_PIN = 17
        self.DC_PIN = 25
        self.CS_PIN = 8
        self.BUSY_PIN = 24

        # Set GPIO pins.
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setup(self.RST_PIN, RPi.GPIO.OUT)
        RPi.GPIO.setup(self.DC_PIN, RPi.GPIO.OUT)
        RPi.GPIO.setup(self.CS_PIN, RPi.GPIO.OUT)
        RPi.GPIO.setup(self.BUSY_PIN, RPi.GPIO.IN)

        # SPI device.
        self.__spi = spidev.SpiDev(0, 0)

        # Set SPI device.
        self.__spi.max_speed_hz = 2000000
        self.__spi.mode = 0b00

    def read_pin(self, pin: int) -> bool:
        """
        Reads the value for a given pin number.

        :param pin: The pin number.
        :type pin: int
        :return The value on the pin.
        :rtype bool
        """
        return RPi.GPIO.input(pin)

    def write_pin(self, pin: int, value: bool):
        """
        Writes a value to a given pin number.

        :param pin: The pin number.
        :type pin: int
        :param value: The value for the pin.
        :type value: bool
        """
        RPi.GPIO.output(pin, value)

    def __transfer(self, data: int):
        """
        Transfers data to the display through the SPI device.

        :param data: Numerical data to send.
        :type data: int
        """
        self.__spi.writebytes(data)

    def send_command(self, command: str or int, command_name=True):
        """
        Sends a command to the device. If command_name equals True, it is used as a key to retreive the command code from the commands dictionnary. Otherwise command is sent as it is.

        :param command: A command key or an actual command to send.
        :type command: str or int
        :param command_name: Determines if the command must be retreived from the commands dictionnary (default is True).
        :type command_name: bool
        """
        self.write_pin(self.DC_PIN, RPi.GPIO.LOW)
        self.__transfer([self.__commands[command] if command_name else command])

    def send_data(self, data: int):
        """
        Sends data to the device.

        :param data: The data to send.
        :type data: int
        """
        self.write_pin(self.DC_PIN, RPi.GPIO.HIGH)
        self.__transfer([data])


class Display:
    def __init__(self, width: int, height: int, interface: DisplayInterface):
        """
        Creates a Display object. It is used upon the Display Interface as an interface to the device's commands. It only needs the device dimensions and the display interface.

        :param width: The width of the device.
        :type width: int
        :param height: The height of the device.
        :type height: int
        :param interface: The display interface.
        :type interface: DisplayInterface
        """
        self.__width = width
        self.__height = height

        self.__interface = interface

        self.__sleeping = True

        self.init()

    @property
    def width(self) -> int:
        """
        Getter for the device's width.

        :rtype int
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Getter for the device's height.

        :rtype int
        """
        return self.__height

    @property
    def is_sleeping(self) -> bool:
        """
        Getter for the device sleep state. This property is kinda artificial as it is set only on reset/sleep calls and do not rely on an actual device information.

        :rtype bool
        """
        return self.__sleeping

    @property
    def is_busy(self) -> bool:
        """
        Getter for the device state.

        :rtype bool
        """
        return self.__interface.read_pin(self.__interface.BUSY_PIN) == 0 # 0: busy, 1: idle.

    def wait_until_idle(self):
        """
        Pauses the process until the device is ready to accept new informations.
        """
        while True:
            time.sleep(self.__interface.WT_STATE_LOOKUP)

            if not self.is_busy:
                break

    def reset(self):
        """
        Resets the device. Its use is not recommanded since the device may need to be reconfigured. Initialization is the recommanded way to get the device out of sleep state.
        """
        self.wait_until_idle()
        self.__interface.write_pin(self.__interface.RST_PIN, RPi.GPIO.LOW)
        time.sleep(self.__interface.WT_PIN_TOGGLE)
        self.__interface.write_pin(self.__interface.RST_PIN, RPi.GPIO.HIGH)
        time.sleep(self.__interface.WT_PIN_TOGGLE)

        self.__sleeping = False

    def init(self):
        """
        Resets the device and reconfigures it.
        """
        self.reset()

        self.__interface.send_command('POWER_SETTING')
        self.__interface.send_data(0x37)
        self.__interface.send_data(0x00)

        self.__interface.send_command('PANEL_SETTING')
        self.__interface.send_data(0xCF)
        self.__interface.send_data(0x08)

        self.__interface.send_command('BOOSTER_SOFT_START')
        self.__interface.send_data(0xc7)
        self.__interface.send_data(0xcc)
        self.__interface.send_data(0x28)

        self.__interface.send_command('POWER_ON')
        self.wait_until_idle()

        self.__interface.send_command('PLL_CONTROL')
        self.__interface.send_data(0x3c)

        self.__interface.send_command('TEMPERATURE_CALIBRATION')
        self.__interface.send_data(0x00)

        self.__interface.send_command('VCOM_AND_DATA_INTERVAL_SETTING')
        self.__interface.send_data(0x77)

        self.__interface.send_command('TCON_SETTING')
        self.__interface.send_data(0x22)

        self.__interface.send_command('TCON_RESOLUTION')
        self.__interface.send_data(0x02) #source 640
        self.__interface.send_data(0x80)
        self.__interface.send_data(0x01) #gate 384
        self.__interface.send_data(0x80)

        self.__interface.send_command('VCM_DC_SETTING')
        self.__interface.send_data(0x1E) #decide by LUT file

        self.__interface.send_command(0xe5, False) #FLASH MODE
        self.__interface.send_data(0x03)

    def sleep(self):
        """
        Puts the device in sleep mode.
        """
        if not self.is_sleeping:
            self.wait_until_idle()
            self.__interface.send_command('POWER_OFF')
            self.wait_until_idle()
            self.__interface.send_command('DEEP_SLEEP')
            self.__interface.send_data(0xa5)

            self.__sleeping = True

    def display_frame(self, pixels):
        """
        Sends a frame to the device and refreshes the display.

        :param pixels: The pixels matrix, typically PIL's PixelAccess object.
        :raise EPDExceptions.InvalidDisplayStatusException: Raised if the display is sleeping.
        """
        if self.is_sleeping:
            raise EPDExceptions.InvalidDisplayStatusException('Display is sleeping')

        self.wait_until_idle()
        self.__interface.send_command('DATA_START_TRANSMISSION_1')

        for y in range(self.height):
            x = 0

            while x < self.width:
                data = 0x00

                if pixels[x, y]:
                    data += 0x30

                if pixels[x + 1, y]:
                    data += 0x03

                self.__interface.send_data(data)

                x += 2

        self.__interface.send_command('DISPLAY_REFRESH')
        self.wait_until_idle()
