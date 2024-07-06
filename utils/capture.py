import bettercam
from screeninfo import get_monitors


def get_primary_display_resolution():
    _ = get_monitors()
    for m in _:
        if m.is_primary:
            return m.width, m.height


class Capture:
    def __init__(self):
        self._custom_region = []
        self._offset_x = None
        self._offset_y = None

        self.screen_x_center = int(384 / 2)
        self.screen_y_center = int(216 / 2)

        self.prev_detection_window_width = 384
        self.prev_detection_window_height = 216
        self.prev_bettercam_capture_fps = 60

        self.bc = bettercam.create(device_idx=0, output_idx=0, output_color="BGR", max_buffer_len=64,
                                   region=self.calculate_screen_offset())
        if not self.bc.is_capturing:
            self.bc.start(region=self.calculate_screen_offset(custom_region=self._custom_region,
                                                              x_offset=self._offset_x,
                                                              y_offset=self._offset_y),
                          target_fps=self.prev_bettercam_capture_fps)

    def get_new_frame(self):
        return self.bc.get_latest_frame()

    def calculate_screen_offset(self, custom_region=None, x_offset=None, y_offset=None):
        if custom_region is None:
            custom_region = []
        if x_offset is None:
            x_offset = 0
        if y_offset is None:
            y_offset = 0

        if len(custom_region) <= 0:
            left, top = get_primary_display_resolution()
        else:
            left, top = custom_region

        left = left / 2 - self.prev_detection_window_width / 2 + x_offset
        top = top / 2 - self.prev_detection_window_height / 2 - y_offset
        width = left + self.prev_detection_window_width
        height = top + self.prev_detection_window_height

        return int(left), int(top), int(width), int(height)


capture = Capture()
