import torch
from ultralytics import yolo
from ultralytics.yolo.utils.torch_utils import select_device
from ultralytics.nn.tasks import attempt_load_one_weight
from ultralytics.yolo.utils.ops import non_max_suppression as nms_v2


class Detector:
    def __init__(self):
        self.device = self._select_device()

    def _select_device(self):
        device = ''
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                if device != '':
                    device += ','
                device = str(i)
        return select_device(device)

    def _load_model(self, weights=''):
        model, _ = attempt_load_one_weight(weights, self.device)
        return model

    def detect_image(self, model, img, confidence, classes):
        pred = model(img, augment=False)[0]
        pred = self._apply_nms(pred, confidence, classes)

        if pred is None:
            pred = []

        return pred

    def _apply_nms(self, pred, confidence, classes):
        return nms_v2(pred, confidence, 0.45, classes=classes, agnostic=True)


class Utils:
    @staticmethod
    def check_frame_rate(frame_rate):
        if frame_rate is None:
            frame_rate = int(1)
        return frame_rate


if __name__ == "__main__":
    # Example usage
    detector = Detector()
    image = torch.rand(1, 3, 416, 416)  # Example image tensor
    confidence_threshold = 0.5
    target_classes = [0, 1, 2]  # Example target classes
    detection_results = detector.detect_image(image, confidence_threshold, target_classes)
    print(detection_results)




