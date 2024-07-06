import win32api

from ultralytics import YOLO

from utils.capture import capture
from utils.frame_parser import frameParser


def perform_detection(model, image):
    return model.predict(
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


def init():
    try:
        model = YOLO(f'models/gemborant.pt', task='detect')
    except Exception as e:
        print('An error occurred when loading the AI model:\n', e)
        quit(0)

    while True:
        if (
                win32api.GetAsyncKeyState(0x41) == 0
                and win32api.GetAsyncKeyState(0x44) == 0
                and win32api.GetAsyncKeyState(0x57) == 0
                and win32api.GetAsyncKeyState(0x53) == 0):
            image = capture.get_new_frame()

            result = perform_detection(model, image)

            frameParser.parse(result)


if __name__ == '__main__':
    init()
