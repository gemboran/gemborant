import cv2
import numpy as np
import time
from mss import mss
import threading


class Capture:
    def __init__(self, x, y, x_fov, y_fov):
        self.x, self.y, self.x_fov, self.y_fov = x, y, x_fov, y_fov
        self.screen = np.zeros((x_fov, y_fov, 3), np.uint8)
        self.image = None
        self.lock = threading.Lock()
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        self.start_time = time.time()
        self.frame_count = 0

    def capture_loop(self):
        while True:
            with self.lock:
                self.capture_screen()
            self.update_fps()

    def capture_screen(self):
        with mss() as sct:
            monitor = {"top": self.y, "left": self.x, "width": self.x_fov, "height": self.y_fov, "monitor": 0}
            self.image = sct.grab(monitor)
            self.screen = np.array(self.image)

    def update_fps(self):
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 1:
            fps = self.frame_count / elapsed_time
            print(f" - FPS: {fps:.0f}", end="\r")
            self.frame_count = 0
            self.start_time = time.time()

    def get_screen(self):
        with self.lock:
            return cv2.cvtColor(self.screen, cv2.COLOR_BGRA2BGR)
