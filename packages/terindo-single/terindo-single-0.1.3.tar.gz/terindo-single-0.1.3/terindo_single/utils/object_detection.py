from ultralytics import YOLO, NAS
import supervision as sv

class YoloObjectDetector:
    def __init__(self, model_path, classes, conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.classes = classes
        self.conf_threshold = conf_threshold

    def detect_objects(self, image_path, classes=None, line=False,):
        """
        Detects objects in an image and returns the bounding boxes, class labels, and confidence scores.
        
        Args:
            image_path (str): The path to the image file.
            classes (list, optional): The list of classes to detect. If not specified, the classes defined
                in the object detector will be used. Defaults to None.
            line (bool, optional): Whether to perform line detection or not. If line detection is enabled,
                the function will also return the line detections. Defaults to False.
        
        Returns:
            tuple: A tuple containing the detected objects and the line detections. If line detection is
                disabled, the line detections will be None.
            bool: False if there was an error during detection.
        """
        
        if classes is None:
            classes = self.classes
        else:
            classes = classes
            
        results = self.model.track(source=image_path, classes=classes, conf=self.conf_threshold, show=False, stream=True, persist=True, agnostic_nms=True, verbose=False)
        output = []

        for result in results:
            if line:
                detections = sv.Detections.from_ultralytics(result)
                if result.boxes.id is not None:
                    detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
                    
            for box in result.boxes[0]:
                x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
                class_id = box.cls[0].item()
                prob = round(box.conf[0].item(), 2)
                output.append([x1, y1, x2, y2, result.names[class_id], prob])
            
            if line:
                return output, detections
            else:
                return output, None
        else:
            return False