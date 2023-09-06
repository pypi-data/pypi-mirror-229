import cv2
import numpy as np
from ultralytics import YOLO
from .geometry import four_point_transform
import matplotlib.pyplot as plt

class YoloObjectSegmentation:
    def __init__(self, model_path, conf_threshold=0.5):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None

    def load_model(self):
        """
        Loads the model for the object detection task.

        Returns:
            bool: True if the model is successfully loaded, False otherwise.
        """
        try:
            self.model = YOLO(self.model_path, task='segment')
        except FileNotFoundError:
            print("Model file not found. Please check the file path.")
            return False
        return True

    def process_single_image(self, image_path):
        """
        Process a single image.

        Args:
            image_path (str): The path to the image file.

        Returns:
            list: A list of tuples containing the processed data. Each tuple consists of a status and a warped image.

        Raises:
            Exception: If there is an error loading the model.
            Exception: If there is an error segmenting the image.
            Exception: If there are no results.
            Exception: If there are no contours found in the image.
            Exception: If there is an error warping the image.
        """
        processed_data = []  # Store processed data as (status, warped_image) tuples
        H = 0
        W = 0
        
        if self.model is None and not self.load_model():
            print("Error loading model.")
            return processed_data

        try:
            results = self.model(image_path, conf=self.conf_threshold, verbose=False)
            H, W, _ = image_path.shape
            
        except Exception as e:
            print(f"Error segmentasi on image : {e}")
            processed_data.append(("failure", None))
            return processed_data


        if results is None:
            print(f"Error results")
            processed_data.append(("failure", None))
            return processed_data
                
        for result in results:
            # print(f"result: {result}")
            if result.masks is None:
                print(f"Error result.masks.data")
                processed_data.append(("failure", None))
                continue

                
            for j, mask in enumerate(result.masks.data):

                # print(f"mask: {mask}")
                mask = mask.numpy() + 255
                mask = mask.astype(np.uint8)
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                mask = cv2.resize(mask, (W, H))
                erosion_size = 10
                kernel = np.ones((erosion_size, erosion_size), np.uint8)
                eroded_mask = cv2.erode(mask, kernel)
                data = image_path.copy()
                data = cv2.addWeighted(data, 1, eroded_mask, 1, 0)
                gray = cv2.cvtColor(data, cv2.COLOR_RGB2GRAY)
                _, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)
                
                try:
                    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # # show 4 point contour red dot
                    # for i in range(len(largest_contour)):
                    #     cv2.circle(data, (largest_contour[i][0][0], largest_contour[i][0][1]), 5, (0, 0, 255), -1)
                    
                    
                except Exception as e:
                    print(f"No contours found in image .")
                    processed_data.append(("failure", None))
                    continue

                try:
                    
                    epsilon = 0.05 * cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                    
                    if len(approx) == 4:
                        pts = np.array(approx).reshape(4, 2)
                        warped = four_point_transform(data, pts)
                        
                        processed_data.append(("success", warped))
                except Exception as e:
                    print(f"Error {e}")
                    processed_data.append(("failure", None))
                    
        return processed_data

