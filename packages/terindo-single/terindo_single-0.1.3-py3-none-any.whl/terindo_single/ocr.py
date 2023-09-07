import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO
from .utils.ocr_process import OcrProcess
from .utils.memory_cleanup import register_cleanup

class Ocr:
    def __init__(self, 
                 ocr_recognition_model_dir, 
                 ocr_detection_model_dir, 
                 char_dict_path):
       
        self.ocr_recognition_model_dir = ocr_recognition_model_dir
        self.ocr_detection_model_dir = ocr_detection_model_dir
        self.character_dict_path = char_dict_path
 

        self.ocr_processor = OcrProcess(
            rec_model_dir=self.ocr_recognition_model_dir,
            det_model_dir=self.ocr_detection_model_dir,
            char_dict_path=self.character_dict_path
        )
        
        self.objects_to_clean = [self.ocr_processor]
            
        register_cleanup(self.objects_to_clean)
            
    def process_image(self, image_or_base64):
        
        status = False
        plat_kendaraan = "error"
        
        try:
            if isinstance(image_or_base64, str):
                image_data = base64.b64decode(image_or_base64)
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_or_base64, np.ndarray):
                image = Image.fromarray(image_or_base64)
               
            else:
                print("Invalid image type")
                return status, plat_kendaraan

            try:
                
                image_data = np.array(image)
                image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
                image_data = cv2.resize(image_data, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                
                ocr_result = self.ocr_processor.run_ocr(image_data)
                last_item = ocr_result[0][0]  
                plat_kendaraan = last_item[1][0]

                
                status = True
            except Exception as ocr_exception:
                print("OCR exception:", ocr_exception)
                plat_kendaraan = "error"
                status = False
          
        
            return status, plat_kendaraan
            
        except Exception as e:
            print("error : ", e)
            return status, plat_kendaraan
