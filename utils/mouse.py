import time
import serial


class MouseThread:
    def __init__(self):
        self.bScope = False
        self.button_pressed = False
        self.pov_x = 45
        self.pov_y = 45
        self.screen_width = 320
        self.screen_height = 320
        self.center_x = self.screen_width / 2
        self.center_y = self.screen_height / 2
        self.prev_time = None
        self.prev_x = 0
        self.prev_y = 0
        self.serial = serial.Serial()
        self.serial.baudrate = 115200
        self.serial.timeout = 1
        self.serial.port = self.find_serial_port()
        self.serial.open()

    def find_serial_port(self):
        port = next((port for port in serial.tools.list_ports.comports() if "SERIAL" in port.description), None)
        if port is not None:
            return port.device
        else:
            print('Unable to find serial port or the Arduino device is with different name. Please check its connection and try again.')

    def process_data(self, data):
        target_x, target_y, target_w, target_h = data
        self.bScope = self.check_target_in_scope(target_x, target_y, target_w, target_h)
        current_time = time.time()
        target_x, target_y = self.predict_target_position(target_x, target_y, current_time)
        target_x, target_y = self.calc_movement(target_x, target_y)
        self.move_mouse(target_x, target_y)
        self.shoot(True)

    def predict_target_position(self, target_x, target_y, current_time):
        if self.prev_time is None:
            self.prev_time = current_time
            self.prev_x = target_x
            self.prev_y = target_y
            return target_x, target_y

        delta_time = current_time - self.prev_time
        velocity_x = (target_x - self.prev_x) / delta_time
        velocity_y = (target_y - self.prev_y) / delta_time
        predicted_x = target_x + velocity_x * delta_time
        predicted_y = target_y + velocity_y * delta_time
        self.prev_time = current_time
        self.prev_x = target_x
        self.prev_y = target_y
        return predicted_x, predicted_y

    def calc_movement(self, target_x, target_y):
        offset_x = target_x - self.center_x
        offset_y = target_y - self.center_y
        degrees_per_pixel_x = self.pov_x / self.screen_width
        degrees_per_pixel_y = self.pov_y / self.screen_height
        mouse_move_x = offset_x * degrees_per_pixel_x
        mouse_move_y = offset_y * degrees_per_pixel_y
        move_x = (mouse_move_x / 360) * (1000 * (1 / 0.6))
        move_y = (mouse_move_y / 360) * (1000 * (1 / 0.6))
        return move_x, move_y

    def check_target_in_scope(self, target_x, target_y, target_w, target_h):
        reduced_w = target_w * 0.6 / 2
        reduced_h = target_h * 0.6 / 2

        x1 = target_x - reduced_w
        x2 = target_x + reduced_w
        y1 = target_y - reduced_h
        y2 = target_y + reduced_h

        return x1 < self.center_x < x2 and y1 < self.center_y < y2

    def move_mouse(self, x, y):
        if x is None or y is None:
            return
        x = x + 256 if x < 0 else x
        y = y + 256 if y < 0 else y
        self.serial.write(b"M" + bytes([int(x), int(y)]))

    def shoot(self, shoot):
        if self.bScope:
            delay = random.uniform(0.010, 0.100)
            if shoot:
                self.serial.write(b"P")
                time.sleep(delay)
                self.serial.write(b"R")
            else:
                self.serial.write(b"R")
            time.sleep(delay)


mouse = MouseThread()
