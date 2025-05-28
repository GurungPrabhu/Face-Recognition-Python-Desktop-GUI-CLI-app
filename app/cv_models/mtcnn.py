from mtcnn import MTCNN
import numpy as np
import cv2


class MTCNNFaceDetector:
    CONFIG = {
        "threshold_pnet": 0.6,
        "threshold_rnet": 0.7,
        "threshold_onet": 0.9,
        "min_face_size": 30,
    }

    def __init__(self):
        self.detector = MTCNN()

    def detect_faces(self, data: np.ndarray):
        if isinstance(data, np.ndarray):
            # Convert to RGB if image is in BGR (OpenCV)
            if data.shape[-1] == 3:  # Image should be H x W x 3
                image_rgb = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            else:
                print("Invalid image shape.")
                return []

            return self.detector.detect_faces(
                image_rgb,
                threshold_pnet=self.CONFIG["threshold_pnet"],
                threshold_rnet=self.CONFIG["threshold_rnet"],
                threshold_onet=self.CONFIG["threshold_onet"],
                min_face_size=self.CONFIG["min_face_size"],
            )
        else:
            print("Unsupported data type. Expected NumPy array.")
            return []
