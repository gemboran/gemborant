import cv2
import numpy as np
import threading
import time
import win32api
import pyautogui
import serial
import serial.tools.list_ports

from capture import Capture
from mouse import AHKMouse, ArduinoMouse
from fov_window import show_detection_window, toggle_window

class Colorant:
    LOWER_COLOR = np.array([140, 120, 180])
    UPPER_COLOR = np.array([160, 200, 255])

    def __init__(self, x, y, xfov, yfov, FLICKSPEED, MOVESPEED):
        self.arduinomouse = AHKMouse()
        self.grabber = Capture(x, y, xfov, yfov)
        self.flickspeed = FLICKSPEED
        self.movespeed = MOVESPEED
        threading.Thread(target=self.listen, daemon=True).start()
        self.toggled = False
        self.window_toggled = False
        
    def toggle(self):
        self.toggled = not self.toggled
        time.sleep(0.2)

    def listen(self):
        while True:
            # check if a s d w not pressed, click
            if win32api.GetAsyncKeyState(0x41) == 0 and win32api.GetAsyncKeyState(0x44) == 0 and win32api.GetAsyncKeyState(0x57) == 0 and win32api.GetAsyncKeyState(0x53) == 0 and self.toggled:
                # self.process("move")
                self.process("flick")
            if win32api.GetAsyncKeyState(0x71) < 0:
                toggle_window(self)
                time.sleep(0.2)

    def process(self, action):
        screen = self.grabber.get_screen()
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
        dilated = cv2.dilate(mask, None, iterations=5)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return

        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        center = (x + w // 2, y + h // 2)
        y_offset = int(h * 0.3)

        if action == "move":
            cX = center[0]
            cY = y + y_offset
            x_diff = cX - self.grabber.xfov // 2
            y_diff = cY - self.grabber.yfov // 2
            self.arduinomouse.move(x_diff * self.movespeed, y_diff * self.movespeed)
            self.process("click")

        elif action == "click" and abs(center[0] - self.grabber.xfov // 2) <= 4 and abs(center[1] - self.grabber.yfov // 2) <= 10:
            self.arduinomouse.click()

        elif action == "flick":
            cX = center[0] + 2
            cY = y + y_offset
            x_diff = cX - self.grabber.xfov // 2
            y_diff = cY - self.grabber.yfov // 2
            flickx = x_diff * self.flickspeed
            flicky = y_diff * self.flickspeed
            self.arduinomouse.flick(flickx, flicky)
            self.arduinomouse.click()

    def close(self):
        self.toggled = False
        self.window_toggled = False
        self.arduinomouse.close()
