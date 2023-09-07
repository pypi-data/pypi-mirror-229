from paddleocr import PaddleOCR
import cv2
from PIL import Image
import numpy as np  # Tambahkan impor ini

class OcrProcess:
    def __init__(self, rec_model_dir, det_model_dir, char_dict_path):
        self.custom_ocr = None
        self.rec_model_dir = rec_model_dir
        self.det_model_dir = det_model_dir
        self.char_dict_path = char_dict_path
        self.initialize_ocr()

    def initialize_ocr(self):
        """
        Initializes the OCR (Optical Character Recognition) for the object.

        Parameters:
            None

        Returns:
            None
        """
        if self.custom_ocr is None:
            self.custom_ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                rec_model_dir=self.rec_model_dir,
                det_model_dir=self.det_model_dir,
                rec_char_dict_path=self.char_dict_path,  # Menggunakan path kamus karakter
                use_gpu=False,
                show_log=False
            )

    def preprocess_image(self, image_data, dpi=300):
        """
        Preprocesses an image by resizing, converting to grayscale, resizing again, and applying a bilateral filter.

        Args:
            image_data (numpy.ndarray): The input image data.
            dpi (int): The DPI (dots per inch) for resizing the image. Default is 300.

        Returns:
            numpy.ndarray: The preprocessed image data.
        """
        image_data = cv2.resize(image_data, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        image_data = Image.fromarray(image_data).resize((int(image_data.shape[1] * 300 / dpi), int(image_data.shape[0] * 300 / dpi)), resample=Image.LANCZOS)
        image_data = cv2.bilateralFilter(np.asarray(image_data),9,75,75)
        return image_data

    def run_ocr(self, image_data):
        """
        Run Optical Character Recognition (OCR) on the given image data.

        Parameters:
            image_data (bytes): The image data to perform OCR on.

        Returns:
            str: The result of the OCR operation.
        """
        result = self.custom_ocr.ocr(image_data)

        return result