import serial.tools.list_ports
import random
import time
import sys
from termcolor import colored
from ahk import AHK

from utils.arduino import *


class ArduinoMouse:
    def __init__(self, filter_length=3):
        self.serial = Arduino(port=self.find_serial_port(), baudrate=115200)
        self.filter_length = filter_length
        self.x_history = [0] * filter_length
        self.y_history = [0] * filter_length

    @staticmethod
    def find_serial_port():
        port = next((port for port in serial.tools.list_ports.comports() if "SERIAL" in port.description), None)
        if port is not None:
            return port.device
        else:
            print(colored('[Error]', 'red'), colored(
                'Unable to find serial port or the Arduino device is with different name. Please check its connection '
                'and try again.',
                'white'))
            time.sleep(10)
            # sys.exit()

    def move(self, x, y):
        self.x_history.append(x)
        self.y_history.append(y)

        self.x_history.pop(0)
        self.y_history.pop(0)

        smooth_x = int(sum(self.x_history) / self.filter_length)
        smooth_y = int(sum(self.y_history) / self.filter_length)

        print(smooth_x, smooth_y)
        self.serial.move(int(smooth_x), int(smooth_y))

    def flick(self, x, y):
        self.serial.move(int(x), int(y))

    def click(self):
        delay = random.uniform(0.01, 0.1)
        self.serial.click()
        time.sleep(delay)

    def press(self):
        self.serial.press()

    def release(self):
        self.serial.release()

    def close(self):
        self.serial.close()

    def __del__(self):
        self.close()


# noinspection PyBroadException
class AHKMouse:
    def __init__(self, filter_length=3):
        self.filter_length = filter_length
        self.x_history = [0] * filter_length
        self.y_history = [0] * filter_length
        try:
            self.ahk = AHK(executable_path='C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe')
            self.arduino = ArduinoMouse()
        except Exception:
            print(colored('[Error]', 'red'),
                  colored('AHK is not installed or not in PATH. Please install AHK and add it to PATH before retrying.',
                          'white'))
            time.sleep(10)
            sys.exit()

    def move(self, x, y):
        self.arduino.move(x, y)
        time.sleep(0.001)

    def flick(self, x, y):
        self.arduino.flick(x, y)
        time.sleep(0.001)

    def click(self):
        delay = random.uniform(0.010, 0.100)
        self.arduino.click()
        time.sleep(delay)

    @staticmethod
    def close():
        time.sleep(0.001)

    def __del__(self):
        self.close()
