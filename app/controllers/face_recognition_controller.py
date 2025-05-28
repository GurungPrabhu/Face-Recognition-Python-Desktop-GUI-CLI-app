import base64
import pickle
import time
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication

from models import FaceDetection
from models import UserRepository, AttendanceRepository
from core import DETECTION_THRESHOLD
from thread import VideoCaptureThread


class FaceRecognitionController(QObject):
    def __init__(self, ctx):
        super().__init__()

        self.ctx = ctx
        self.f_detector = FaceDetection()
        self.repository = UserRepository(ctx)
        self.attendance_repostiory = AttendanceRepository(ctx)
        self.user_list = self.attendance_repostiory.get_users_not_present_today()

        self.video_thread = None
        self.current_frame = None

    def _open_camera(self):
        """Initialize and start camera thread"""
        if self.video_thread is None:
            self.video_thread = VideoCaptureThread(self.ctx)
            self.video_thread.frame_ready.connect(self._update_frame)
            self.video_thread.start()
        self.current_frame = None
        self.frame_ready = False

    @pyqtSlot(object)
    def _update_frame(self, frame):
        """Slot to receive frames from camera thread"""
        self.current_frame = frame
        self.frame_ready = True

    @staticmethod
    def decode_embedding(encoded_embedding: str):
        return pickle.loads(base64.b64decode(encoded_embedding.encode("utf-8")))

    def update_frame(self):
        """Fetches the current frame from the video feed."""
        self._open_camera()
        ret, frame = self.cap.read()
        frame_with_box = self.f_detector.detect_faces(frame)
        if not ret:
            return None

        return frame_with_box

    def _capture_face_embedding(self, app=None):
        """Wait for a valid face embedding from camera"""
        start_time = time.time()
        timeout = 5
        while time.time() - start_time < timeout:
            if self.current_frame is not None:
                _, embedding = self.f_detector.detect_faces(self.current_frame.copy())
                if embedding is not None:
                    return embedding

            if app is not None:
                app.processEvents()
            else:
                QApplication.processEvents()
            QThread.msleep(50)

        raise Exception("No face detected within timeout period")

    def detect_user_by_face(self, image_path=None):
        """Detects users by comparing face embeddings."""
        if image_path:
            frame = cv2.imread(image_path)
            if frame is None:
                raise Exception("Error: Could not read image from the provided path.")
            _, encoded_face = self.f_detector.detect_faces(frame)
        else:
            self._open_camera()
            try:
                encoded_face = self._capture_face_embedding()
            finally:
                self.release()

        user_list = self.repository.get_all()
        result = []

        for user in user_list:
            decoded_embedding = self.decode_embedding(user.face_embedding)
            match = False
            if (
                isinstance(decoded_embedding, list)
                and len(decoded_embedding) > 0
                and len(encoded_face) > 0
                and isinstance(decoded_embedding[0], torch.Tensor)
            ):
                match, sim = self.f_detector.match_face(
                    decoded_embedding[0], encoded_face[0], threshold=DETECTION_THRESHOLD
                )
                if match:
                    self.attendance_repostiory.mark_attendance(user.id, True)
                    result.append(user.user_name)

        return result

    def authorize_face(self, image_path=None):
        if image_path:
            frame = cv2.imread(image_path)
            if frame is None:
                raise Exception("Error: Could not read image from the provided path.")
            _, encoded_face = self.f_detector.detect_faces(frame)
        else:

            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                is_new_app = True
            else:
                is_new_app = False
            QThread.msleep(100)
            self._open_camera()

            try:
                start_time = time.time()
                timeout = 5
                encoded_face = None

                while time.time() - start_time < timeout:
                    if self.current_frame is not None:
                        # Process the frame
                        _, encoded_face = self.f_detector.detect_faces(
                            self.current_frame.copy()
                        )
                        if (
                            encoded_face is not None
                        ):  # Exit from loop if face is detected
                            break

                    # Process events and wait briefly
                    if is_new_app:
                        app.processEvents()
                    else:
                        QApplication.processEvents()
                    QThread.msleep(300)
                else:
                    raise Exception("Timeout: No face detected in camera feed")

            finally:
                if is_new_app:
                    app.quit()  # Clean up if we created the QApplication

        user_list = []

        self.user_list = self.attendance_repostiory.get_users_not_present_today()
        for user in self.user_list:
            decoded_embedding = self.decode_embedding(user.face_embedding)
            match = False
            if (
                isinstance(decoded_embedding, list)
                and len(decoded_embedding) > 0
                and len(encoded_face) > 0
                and isinstance(decoded_embedding[0], torch.Tensor)
            ):
                match, _ = self.f_detector.match_face(
                    decoded_embedding[0], encoded_face[0], threshold=DETECTION_THRESHOLD
                )
                if match:
                    print("INFO: match found with user: ", user.user_name)
                    self.attendance_repostiory.mark_attendance(user.id, True)
                    self.user_list.remove(user)
                    user_list.append(user.user_name)

        return user_list

    def release(self):
        """Releases the video capture when done."""
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread = None
        self.current_frame = None
        self.frame_ready = False

    def get_users_preset_today(self):
        """Get the list of users who are present today."""
        return self.attendance_repostiory.get_users_present_today()
