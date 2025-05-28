import cv2
import torch
import numpy as np
import torch.nn.functional as F
from cv_models import MTCNNFaceDetector, FaceEncoder


class FaceDetection:
    def __init__(self):
        self.face_detector = MTCNNFaceDetector()
        self.encoder = FaceEncoder()

        self.user_list = None

    def detect_user(self, user_list):
        self.user_list = user_list

    def detect_faces(self, data: np.ndarray):
        """
        Detect faces from either an image or video frame data and add bounding box.

        Parameters:
        - data: Either an image (NumPy array) or a video frame (NumPy array).

        Returns:
        - image_with_boxes: The frame/image with bounding boxes drawn.
        - encoded_face: Encoded face.
        """
        if isinstance(data, np.ndarray):
            # Detect faces in the image/frame
            faces = self.face_detector.detect_faces(data)

            encoded_face = self.encoder.process_faces(data, faces)
            # Draw bounding boxes on the image/frame

            image_with_names = self.draw_predicted_name(faces, encoded_face, data)
            image_with_boxes = self.draw_faces(faces, image_with_names)

            return image_with_boxes, encoded_face
        else:
            print("ERROR: Unsupported data type. Expected a NumPy array.")
            return None

    def draw_faces(self, faces, image):
        """
        Draw bounding boxes, landmarks, and additional information around detected faces on the image.

        Parameters:
        - faces: List of detected faces.
        - image: Original image/frame.

        Returns:
        - image_with_boxes: Image/frame with bounding boxes, landmarks, and information.
        """
        image_with_boxes = image.copy()  # To keep the original image unchanged

        # Draw bounding boxes around faces
        image_with_boxes = self.draw_bounding_boxes(faces, image_with_boxes)

        # Draw landmarks (optional)
        image_with_boxes = self.draw_landmarks(faces, image_with_boxes)

        # Draw face detection information (like confidence and face count)
        image_with_boxes = self.draw_information(faces, image_with_boxes)

        return image_with_boxes

    def draw_bounding_boxes(self, faces, image):
        """
        Draw bounding boxes around detected faces.

        Parameters:
        - faces: List of detected faces.
        - image: Original image/frame.

        Returns:
        - image_with_boxes: Image/frame with bounding boxes drawn.
        """
        green = (0, 255, 0)  # Color
        thickness = 2

        for face in faces:
            x, y, w, h = face["box"]
            cv2.rectangle(image, (x, y), (x + w, y + h), green, thickness=thickness)

        return image

    def draw_landmarks(self, faces, image):
        """
        Draw landmarks on the detected faces.

        Parameters:
        - faces: List of detected faces.
        - image: Original image/frame.

        Returns:
        - image_with_landmarks: Image/frame with landmarks drawn.
        """
        green = (0, 255, 0)  # Color for landmarks
        thickness = 2

        for face in faces:
            # Extracting landmarks from the detected face
            landmarks = face.get("keypoints", {})
            for key, point in landmarks.items():
                x, y = point
                cv2.circle(image, (x, y), 3, green, thickness)

        return image

    def match_face(
        self, face: torch.Tensor, image: torch.Tensor, threshold: float = 0.5
    ):
        similarity = F.cosine_similarity(face, image, dim=1).item()
        return similarity > threshold, similarity

    def draw_predicted_name(self, faces, embeddings, image):
        """
        Draw predicted face name with percentage .

        Parameters:
        - faces: List of detected faces.
        - embeddings: Original embedding lists .
        - image: Original image/frame.

        Returns:
        - image_with_info: Image/frame with information drawn.
        """
        green = (0, 255, 0)  # Color for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2

        if self.user_list is None:
            return image

        for user in self.user_list:
            decoded_embedding = user.decode_embedding()

            match = False
            if (
                isinstance(decoded_embedding, list)
                and len(decoded_embedding) > 0
                and len(embeddings) > 0
                and isinstance(decoded_embedding[0], torch.Tensor)
            ):
                for i, embedding in enumerate(embeddings):

                    match, sim = self.match_face(
                        decoded_embedding[0], embedding, threshold=0.7
                    )
                    x, y, w, h = faces[i]["box"]
                    if match:
                        cv2.putText(
                            image,
                            f"{user.user_name} Sim: {sim:.2f}",
                            (x + 200, y - 10),
                            font,
                            1,
                            green,
                            thickness,
                            cv2.LINE_AA,
                        )

        return image

    def draw_information(self, faces, image):
        """
        Draw information about detected faces (confidence, face count) on the image.

        Parameters:
        - faces: List of detected faces.
        - image: Original image/frame.

        Returns:
        - image_with_info: Image/frame with information drawn.
        """
        green = (0, 255, 0)  # Color for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2

        # Draw number of detected faces at the bottom
        num_faces = len(faces)
        count_label = f"Detected Faces: {num_faces}"
        img_height = image.shape[0]
        cv2.putText(
            image,
            count_label,
            (10, img_height - 10),
            font,
            0.6,
            green,
            thickness,
            cv2.LINE_AA,
        )

        # Optionally, display confidence for each face
        for i, face in enumerate(faces):
            x, y, w, h = face["box"]
            confidence = face.get("confidence", 0)
            label = f"Conf: {confidence:.2f}"
            cv2.putText(
                image,
                label,
                (x, y - 10),
                font,
                1,
                green,
                thickness,
                cv2.LINE_AA,
            )

        return image
