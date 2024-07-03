import cv2
import numpy as np
import threading
import time
import win32api
import pyautogui
import serial
import serial.tools.list_ports
from ultralytics import YOLO

from capture import Capture
from mouse import AHKMouse, ArduinoMouse
from fov_window import show_detection_window, toggle_window

class Target:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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
        self.model = YOLO(f'gemborant.pt', task='detect')
        
    def toggle(self):
        self.toggled = not self.toggled
        time.sleep(0.2)

    def listen(self):
        while True:
            # check if a s d w not pressed, click
            if win32api.GetAsyncKeyState(0x41) == 0 and win32api.GetAsyncKeyState(0x44) == 0 and win32api.GetAsyncKeyState(0x57) == 0 and win32api.GetAsyncKeyState(0x53) == 0 and self.toggled:
                self.process("move")
                self.process("click")
            if win32api.GetAsyncKeyState(0x71) < 0:
                toggle_window(self)
                time.sleep(0.2)
            # if win32api.GetAsyncKeyState(0x02) < 0 and self.toggled:
            #     self.process("move")
            # elif win32api.GetAsyncKeyState(0x12) < 0 and self.toggled:
            #     self.process("click")
            # elif win32api.GetAsyncKeyState(0x11) < 0 and self.toggled:
            #     self.process("flick")

    def process(self, action):
        screen = self.grabber.get_screen()
        result = self.perform_detection(screen)
        for frame in result:
            if len(frame.boxes):
                target = self.sort_targets(frame)

                x, y, w, h = target.x, target.y, target.w, target.h
                center = (x + w // 2, y + h // 2)
                y_offset = int(h * 0.3)

                if action == "move":
                    cX = center[0]
                    cY = y + y_offset
                    x_diff = cX - self.grabber.xfov // 2
                    y_diff = cY - self.grabber.yfov // 2
                    self.arduinomouse.move(x_diff * self.movespeed, y_diff * self.movespeed)

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
                    self.arduinomouse.flick(-(flickx), -(flicky))

    def close(self):
        self.toggled = False
        self.window_toggled = False
    
    def perform_detection(self, image):
        return self.model.predict(
            source=image,
            stream=True,
            imgsz=320,
            stream_buffer=False,
            visualize=False,
            augment=False,
            agnostic_nms=False,
            save=False,
            iou=0.3,
            half=True,
            max_det=25,
            vid_stride=False,
            verbose=False,
            show_boxes=False,
            show_labels=False,
            show_conf=False,
            show=False)
    
    @staticmethod
    def sort_targets(self, frame) -> Target:
        boxes_array = frame.boxes.xywh.cuda()
        center = torch.tensor([capture.screen_x_center, capture.screen_y_center]).cuda()
        distances_sq = torch.sum((boxes_array[:, :2] - center) ** 2, dim=1)
        classes_tensor = frame.boxes.cls.cuda()
        head_indices = torch.nonzero(classes_tensor == 1, as_tuple=False).squeeze(1)
        if len(head_indices) > 0:
            head_distances_sq = distances_sq[head_indices]
            nearest_head_index = head_indices[torch.argmin(head_distances_sq)]
            return Target(*boxes_array[nearest_head_index, :4].cpu().numpy())
        nearest_index = torch.argmin(distances_sq)
        return Target(*boxes_array[nearest_index, :4].cpu().numpy())
