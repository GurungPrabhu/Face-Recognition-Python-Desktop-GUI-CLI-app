import base64
import pickle
import time
import cv2
from PyQt5.QtCore import pyqtSlot, QObject, QThread
from PyQt5.QtWidgets import QApplication

from thread import VideoCaptureThread
from models import FaceDetection, UserRepository
from cv_models import FaceEncoder
from core import DEBUG


class FaceRegistrationController(QObject):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.repository = UserRepository(ctx)
        self.f_detector = FaceDetection()
        self.encoder = FaceEncoder()

        # Implement separate video thread
        self.video_thread = None
        self.current_frame = None

    def _open_camera(self):
        print("INFO: Opening camera for sign-up")
        self.video_thread = VideoCaptureThread(self.ctx)
        self.video_thread.frame_ready.connect(self._update_current_frame)
        self.video_thread.start()

    @pyqtSlot(object)
    def _update_current_frame(self, frame):
        """Slot to receive frames from the video thread"""
        self.current_frame = frame

    def encode_embedding(self, embedding) -> str:
        """Convert numpy array to a string for database storage."""
        return base64.b64encode(pickle.dumps(embedding)).decode("utf-8")

    def add_user(self, user_name: str, face_embedding):
        """Adds or updates a user in the database with their face embedding."""
        encoded_embedding = self.encode_embedding(face_embedding)
        users = self.repository.get_by_name(user_name)
        if users is not None:
            raise Exception("User already exists")
        try:
            self.repository.add_user(user_name, encoded_embedding)
        except Exception as e:
            raise Exception(f"Failed to add user: {e}")

    def get_embedding(self, image_path=None):
        """Get face embedding from the camera feed or a given image path."""
        if image_path:
            frame = cv2.imread(image_path)
            if frame is None:
                raise Exception(f"Failed to read image from path: {image_path}")
            frame, embedding = self.f_detector.detect_faces(frame)
        else:
            # Using this for CLI mode to run the thread
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                is_new_app = True
            else:
                is_new_app = False

            self._open_camera()

            try:
                start_time = time.time()
                timeout = 5
                embedding = None
                QThread.msleep(300)

                while time.time() - start_time < timeout:
                    if self.current_frame is not None:
                        # Process the frame
                        frame, embedding = self.f_detector.detect_faces(
                            self.current_frame.copy()
                        )
                        if embedding is not None:  # Exit from loop if face is detected
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
                self.release()
                if is_new_app:
                    app.quit()  # Clean up if we created the QApplication

        if DEBUG:
            cv2.imshow("Face Registration", frame)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()

        if embedding is None:
            raise Exception("No face detected in the image")

        return embedding

    def release(self):
        """Releases the video capture when done."""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread = None

        print("INFO: Closing camera and releasing thread")
