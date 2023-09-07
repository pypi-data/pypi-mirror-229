import cv2
import numpy as np
import base64
import tempfile
from PIL import Image
from io import BytesIO
from .utils.object_segmentation import YoloObjectSegmentation
from .utils.memory_cleanup import register_cleanup


class Segmentasi:
    def __init__(self, segmentation_weights):
        
        self.segmentation_weights = segmentation_weights
         
        self.segmentation_plate = YoloObjectSegmentation(
            self.segmentation_weights 
        )
        
        self.objects_to_clean = [self.segmentation_plate]
        
        register_cleanup(self.objects_to_clean)
            
    def process_image(self, image_or_base64):
        
        status = False
        image_result = None
        
        try:
            if isinstance(image_or_base64, str):
                image_data = base64.b64decode(image_or_base64)
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_or_base64, np.ndarray):
                image = Image.fromarray(image_or_base64)
            else:
                print("Invalid segmentasi : image type")
                return status, None

            try:
                temp_image_path = np.array(image)
                
                segmented_data = self.segmentation_plate.process_single_image(temp_image_path)

                if not segmented_data:
                    return status, temp_image_path

                status_segmentasi, image_result = segmented_data[0]

                if status_segmentasi == "success":
                    status = True
                    image_result  = image_result
                else:
                    status = False
                    image_result = image_result
                    
            except Exception as segmentation_exception:
                image_result = image_result
                status = False
                
        
            return status, image_result
            
        except Exception as e:
            return status, image_result
