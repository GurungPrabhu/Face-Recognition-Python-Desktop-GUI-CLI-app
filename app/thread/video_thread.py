from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import torch

from core import AppContext
from models import FaceDetection, UserRepository


# Run video capture in a separate thread
class VideoCaptureThread(QThread):
    frame_ready = pyqtSignal(object)

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.capture = None
        self.running = False
        self.detect_face = False
        self.detect_user = False

        self.f_detector = FaceDetection()
        self.u_repo = UserRepository(ctx)
        self.user_list = self.u_repo.get_all()

    def update_user_list(self):
        self.user_list = self.u_repo.get_all()

    def set_detect_face(self, detect_face: bool):
        self.detect_face = detect_face

    def set_detect_user(self, detect_user: bool):
        self.detect_user = detect_user

    def track_user(self, frame):
        """Set the flags for face detection and user detection."""
        if self.detect_face:
            frame, _ = self.f_detector.detect_faces(frame)
        elif self.detect_user:
            self.f_detector.detect_user(self.user_list)
            frame, _ = self.f_detector.detect_faces(frame)
        return frame

    def run(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Could not open camera.")
            return

        self.running = True
        while self.running:
            ret, frame = self.capture.read()
            frame = self.track_user(frame)
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(50)

    def stop(self):
        self.running = False
        self.wait()  # Wait for thread to finish
        if self.capture:
            self.capture.release()
