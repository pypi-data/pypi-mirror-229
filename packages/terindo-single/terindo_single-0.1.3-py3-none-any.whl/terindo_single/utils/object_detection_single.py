from ultralytics import YOLO

class YoloObjectDetectorSingle:
    def __init__(self, model_path, classes, conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.classes = classes
        self.conf_threshold = conf_threshold

    def detect_objects(self, image_path, classes=None):
        """
        Detects objects in an image using a pre-trained model.

        Args:
            image_path (str): The path to the image file.
            classes (List[str], optional): The list of classes to detect. 
                If None, the default class list will be used. Defaults to None.

        Returns:
            List[List[int, int, int, int, str, float]] or bool: 
                A list of detected objects, each represented as a list [x1, y1, x2, y2, class_name, confidence_score]. 
                If no objects are detected, returns False.
        """
        
        if classes is None:
            classes = self.classes
        else:
            classes = classes
            
        results = self.model.predict(source=image_path, classes=classes, conf=self.conf_threshold, verbose=False)
        output = []
        
        for result in results:
            for box in result.boxes[0]:
                x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
                class_id = box.cls[0].item()
                prob = round(box.conf[0].item(), 2)
                output.append([x1, y1, x2, y2, result.names[class_id], prob])
            
            return output
        else:
            return False