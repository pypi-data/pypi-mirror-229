from ultralytics import YOLO

class YoloObjectClassifier:
    def __init__(self, model_path):
        self.model = YOLO(model_path, task='classify')

    def predict_image(self, image_path):
        """
        Predicts the class of an image given its file path.

        Parameters:
            image_path (str): The file path of the image to be predicted.

        Returns:
            str or None: The predicted class of the image. Returns None if the prediction is unsuccessful.
        """
        results = self.model.predict(image_path, verbose=False)
        result = results[0]

        if result:
            names_dict = result.names
            probs = result.probs.data.tolist()
            
            # Get the highest probability class
            predicted_class = names_dict[probs.index(max(probs))]
            return predicted_class
        else:
            return None