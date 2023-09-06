import numpy as np
import base64
from PIL import Image
from io import BytesIO
from .utils.object_classification import YoloObjectClassifier
from .utils.memory_cleanup import register_cleanup

class Klasifikasi:
    def __init__(self, classification_weights):
        
        self.classification_weights = classification_weights
        
        self.class_plate = YoloObjectClassifier(
            self.classification_weights 
        )

        self.objects_to_clean = [self.class_plate]
            
        register_cleanup(self.objects_to_clean)
            
    def process_image(self, image_or_base64):
        
        status = False
        class_name = "hitam"
        
        try:
            if isinstance(image_or_base64, str):
                image_data = base64.b64decode(image_or_base64)
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_or_base64, np.ndarray):
                image = Image.fromarray(image_or_base64)
            else:
                return status, class_name
            
            try:
                class_name = self.class_plate.predict_image(image)
                if class_name is None:
                    class_name = "hitam"
                
                status = True
                
            except Exception as classification_exception:
                class_name = "hitam"
                status = False
        
            return status, class_name
            
        except Exception as e:
            return status, class_name
