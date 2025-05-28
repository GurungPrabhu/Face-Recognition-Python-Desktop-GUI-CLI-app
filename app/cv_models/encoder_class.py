import cv2
import numpy as np
from facenet_pytorch import InceptionResnetV1
from PIL import Image
import matplotlib.pyplot as plt
import torch


class FaceEncoder:
    def __init__(self, min_face_size=30, threshold=0.4, device="cpu"):
        """
        Initializes the FaceEncoder class with InceptionResNetV1 model and other configurations.

        Parameters:
        - min_face_size: Minimum size of the face to detect.
        - threshold: Threshold for detecting face confidence.
        - device: Device to use for model inference ('cpu' or 'cuda').
        """
        self.device = device
        self.min_face_size = min_face_size
        self.threshold = threshold

        # Initialize the Inception ResNet V1 model for face encoding
        self.model = InceptionResnetV1(pretrained="vggface2").eval().to(device)

    def align_face(self, image, landmarks):
        """
        Aligns a face and visualizes the process using OpenCV

        Args:
            image: Input image (BGR format as numpy array)
            landmarks: Dictionary containing 'left_eye', 'right_eye', and 'nose' points

        Returns:
            aligned_face: Aligned face image
        """
        eyes = [landmarks["left_eye"], landmarks["right_eye"]]
        nose = landmarks["nose"]
        standard_eye_position = [(50, 50), (110, 50)]
        standard_nose_position = (80, 90)

        src_pts = np.array(eyes + [nose], dtype=np.float32)
        dst_pts = np.array(
            standard_eye_position + [standard_nose_position], dtype=np.float32
        )

        matrix, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
        aligned_face = cv2.warpAffine(image, matrix, (160, 160))

        return aligned_face

    def encode_face(self, aligned_face):
        """
        Encode the aligned face using the pre-trained InceptionResNetV1 model.

        Parameters:
        - aligned_face: Aligned face image (NumPy array).

        Returns:
        - encoding: The face encoding vector.
        """
        aligned_face_tensor = self.transform_to_tensor(aligned_face)
        encoding = self.model(aligned_face_tensor)
        return encoding

    def transform_to_tensor(self, image):
        """
        Convert the image to a tensor.

        Parameters:
        - image: The image to be transformed (as a NumPy array).

        Returns:
        - Tensor: The image converted to a tensor.
        """
        image_np = np.array(image)

        # Resize the image using OpenCV
        image_resized = cv2.resize(image_np, (160, 160))

        # Normalize the image (using ImageNet mean and std values for FaceNet)
        mean = [0.5, 0.5, 0.5]
        std = [0.5, 0.5, 0.5]

        # Scale pixel values to [0, 1]
        image_resized = image_resized.astype(np.float32) / 255.0
        image_resized = (image_resized - mean) / std

        # Convert the image to a tensor
        image_tensor = torch.tensor(
            image_resized.transpose(2, 0, 1),
            dtype=torch.float32,
        )  # Convert to [C, H, W]
        image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension

        return image_tensor

    def process_face(self, image, face):
        """
        Process a detected face: align and encode it in a single pipeline.

        Parameters:
        - image: Input image (NumPy array).
        - face: Detected face with landmarks.

        Returns:
        - encoded_face: The encoded face (512D feature vector).
        """
        # Align the face based on landmarks
        aligned_face = self.align_face(image, face["keypoints"])

        # Encode the aligned face
        encoded_face = self.encode_face(aligned_face)

        return encoded_face

    def process_faces(self, image, faces):
        """
        Process multiple detected faces: align and encode each one.

        Parameters:
        - image: Input image (NumPy array).
        - faces: List of detected faces with landmarks.

        Returns:
        - encoded_faces: List of encoded faces (feature vectors).
        """
        encoded_faces = []

        for face in faces:
            encoded_face = self.process_face(image, face)
            encoded_faces.append(encoded_face)

        return encoded_faces
