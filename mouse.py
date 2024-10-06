import serial
import serial.tools.list_ports
import random
import time
import pyautogui
import sys
from termcolor import colored
from ahk import AHK


class ArduinoMouse:
    def __init__(self, filter_length=3):
        self.active = False
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 1
        self.serial_port.port = self.find_serial_port()
        self.filter_length = filter_length
        self.x_history = [0] * filter_length
        self.y_history = [0] * filter_length
        try:
            self.serial_port.open()
            self.active = True
        except serial.SerialException:
            print(colored('[Error]', 'red'), colored(
                'Colorant is already open or serial port in use by another app. Close Colorant and other apps before retrying.',
                'white'))
            time.sleep(10)
            # sys.exit()

    def find_serial_port(self):
        port = next((port for port in serial.tools.list_ports.comports() if "SERIAL" in port.description), None)
        if port is not None:
            return port.device
        else:
            print(colored('[Error]', 'red'), colored(
                'Unable to find serial port or the Arduino device is with different name. Please check its connection and try again.',
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

        finalx = smooth_x + 256 if smooth_x < 0 else smooth_x
        finaly = smooth_y + 256 if smooth_y < 0 else smooth_y
        self.serial_port.write(b"M" + bytes([int(finalx), int(finaly)]))

    def flick(self, x, y):
        x = x + 256 if x < 0 else x
        y = y + 256 if y < 0 else y
        self.serial_port.write(b"M" + bytes([int(x), int(y)]))

    def click(self):
        delay = random.uniform(0.01, 0.1)
        self.serial_port.write(b"C")
        time.sleep(delay)

    def press(self):
        self.serial_port.write(b"P")

    def release(self):
        self.serial_port.write(b"R")

    def close(self):
        self.serial_port.close()

    def __del__(self):
        self.close()


class AHKMouse:
    def __init__(self, filter_length=3):
        self.filter_length = filter_length
        self.x_history = [0] * filter_length
        self.y_history = [0] * filter_length
        try:
            self.arduino = ArduinoMouse()
        except Exception as e:
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
        time.sleep(0.010)
        self.click()

    def click(self):
        delay = random.uniform(0.010, 0.100)
        self.arduino.press()
        time.sleep(delay)
        self.arduino.release()
        time.sleep(delay)

    def close(self):
        self.arduino.close()
        time.sleep(0.001)

    def __del__(self):
        self.close()
