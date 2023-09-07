import numpy as np
import base64
from PIL import Image
from io import BytesIO
from .utils.object_detection_single import YoloObjectDetectorSingle
from .utils.memory_cleanup import register_cleanup

class Detektor:
    def __init__(self, tera_detector_weights, classes=None):
        
        self.detector_weights = tera_detector_weights
        
        if classes is None:
            self.class_detector = [2, 3, 5, 7]
        else:
            self.class_detector = classes
        
        self.detector_object = YoloObjectDetectorSingle(
                self.detector_weights, self.class_detector
            )
            
        self.objects_to_clean = [self.detector_weights]

        # Register cleanup function
        register_cleanup(self.objects_to_clean)
            
    def process_image(self, image_or_base64, classes=None):
        """
        Process an image and return a cropped version.

        Args:
            image_or_base64 (str or np.ndarray): The input image or base64 encoded image.
            classes (list, optional): A list of classes to filter the detected objects.

        Returns:
            tuple: A tuple containing the status of the image processing (bool) and the cropped image (np.ndarray).

        Raises:
            Exception: If there is an error during image processing.

        """
        
        status = False
        cropped_image = None
        
        try:
            if isinstance(image_or_base64, str):
                image_data = base64.b64decode(image_or_base64)
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_or_base64, np.ndarray):
                image = Image.fromarray(image_or_base64)
                
            else:
                return status, None

            try:
                detected_objects = self.detector_object.detect_objects(image_path=image, classes=classes) 
                
                if not detected_objects:
                    image = np.array(image)
                    
                    pass

                else:
                                        
                    first_object = detected_objects[0]
                    x1, y1, x2, y2, _, _ = first_object

                    image = np.array(image)[y1:y2, x1:x2]
                    
                cropped_image = image
                status = True
                
               
            except Exception:
                image_or_base64 = None
                return status, None
              
            return status, cropped_image
            
        except Exception:
            return status, None
    