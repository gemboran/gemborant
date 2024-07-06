import numpy as np
import threading
import time
import win32api
from ultralytics import YOLO
import torch

from utils.capture import Capture
from utils.mouse import AHKMouse
from utils.fov_window import toggle_window


class Target:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Colorant:
    LOWER_COLOR = np.array([140, 120, 180])
    UPPER_COLOR = np.array([160, 200, 255])

    def __init__(self, x, y, x_fov, y_fov, flick_speed, move_speed):
        self.arduino_mouse = AHKMouse()
        self.grabber = Capture(x, y, x_fov, y_fov)
        self.flick_speed = flick_speed
        self.move_speed = move_speed
        threading.Thread(target=self.listen, daemon=True).start()
        self.toggled = False
        self.window_toggled = False
        self.model = YOLO(f'models/gemborant.pt', task='detect')
        self.center_x = x_fov / 2
        self.center_y = y_fov / 2

    def toggle(self):
        self.toggled = not self.toggled
        time.sleep(0.2)

    def listen(self):
        while True:
            # check if A S D W key not pressed, click
            if win32api.GetAsyncKeyState(0x41) == 0 and win32api.GetAsyncKeyState(
                    0x44) == 0 and win32api.GetAsyncKeyState(0x57) == 0 and win32api.GetAsyncKeyState(
                    0x53) == 0 and self.toggled:
                self.process("move")
                self.process("click")
            if win32api.GetAsyncKeyState(0x71) < 0:
                toggle_window(self)
                time.sleep(0.2)

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
                    c_x = center[0]
                    c_y = y + y_offset
                    x_diff = c_x - self.grabber.x_fov // 2
                    y_diff = c_y - self.grabber.y_fov // 2
                    self.arduino_mouse.move(x_diff * self.move_speed, y_diff * self.move_speed)

                elif action == "click" and abs(center[0] - self.grabber.x_fov // 2) <= 4 and abs(
                        center[1] - self.grabber.y_fov // 2) <= 10:
                    self.arduino_mouse.click()

                elif action == "flick":
                    c_x = center[0] + 2
                    c_y = y + y_offset
                    x_diff = c_x - self.grabber.x_fov // 2
                    y_diff = c_y - self.grabber.y_fov // 2
                    flick_x = x_diff * self.flick_speed
                    flick_y = y_diff * self.flick_speed
                    self.arduino_mouse.flick(flick_x, flick_y)
                    self.arduino_mouse.click()

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
            show=False
        )

    def sort_targets(self, frame) -> Target:
        boxes_array = frame.boxes.xywh.cpu()
        center = torch.tensor([self.center_x, self.center_y]).cpu()
        distances_sq = torch.sum((boxes_array[:, :2] - center) ** 2, dim=1)
        classes_tensor = frame.boxes.cls.cpu()
        head_indices = torch.nonzero(classes_tensor == 1, as_tuple=False).squeeze(1)
        if len(head_indices) > 0:
            head_distances_sq = distances_sq[head_indices]
            nearest_head_index = head_indices[torch.argmin(head_distances_sq)]
            return Target(*boxes_array[nearest_head_index, :4].cpu().numpy())
        nearest_index = torch.argmin(distances_sq)
        return Target(*boxes_array[nearest_index, :4].cpu().numpy())
