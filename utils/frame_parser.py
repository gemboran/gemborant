import torch

from utils.capture import capture
from utils.mouse import mouse


class Target:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class FrameParser:
    def __init__(self):
        self.arch = "cuda:0"

    def parse(self, result):
        for frame in result:
            if len(frame.boxes):
                target = self.sort_targets(frame)

                mouse.process_data((target.x, target.y, target.w, target.h))
            else:
                mouse.shoot(False)
                pass

    @staticmethod
    def sort_targets(frame) -> Target:
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


frameParser = FrameParser()
