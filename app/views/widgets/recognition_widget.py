from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
)
from PyQt5.QtCore import QTimer

from thread import DetectFaceThread
from controllers import FaceRecognitionController


class RecognitionWidget(QWidget):
    def __init__(self, parent=None, ctx=None):
        super().__init__(parent)
        self.ctx = ctx
        self.is_detecting = False
        self.setup_ui()
        self.setup_timer()
        self.embedding = None

        self.controller = FaceRecognitionController(ctx)
        self.face_thread = None

    def setup_ui(self):
        """Setup the UI for the Attendance Menu page"""
        self.main_layout = QVBoxLayout()

        title_label = QLabel("Attendance List")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 10px;
            }
            """
        )

        self.recognized_face_list = QListWidget()

        self.name_list_widget = QListWidget()

        self.main_layout.addWidget(title_label)
        name_list_label = QLabel("Today's Attendance List")
        name_list_label.setStyleSheet(
            """
            QLabel {
            font-size: 16px;
            font-weight: bold;
            padding-top: 10px;
            padding-bottom: 5px;
            }
            """
        )
        self.main_layout.addWidget(name_list_label)
        self.main_layout.addWidget(self.name_list_widget)

        recognized_face_label = QLabel("Recognized Faces")
        recognized_face_label.setStyleSheet(
            """
            QLabel {
            font-size: 16px;
            font-weight: bold;
            padding-top: 10px;
            padding-bottom: 5px;
            }
            """
        )
        self.main_layout.addWidget(recognized_face_label)
        self.main_layout.addWidget(self.recognized_face_list)

        self.go_back_button = QPushButton("Go back")
        self.go_back_button.setStyleSheet(
            """
            QPushButton {
            font-size: 16px;
            padding: 5px 10px;
            }
            """
        )
        self.main_layout.addWidget(self.go_back_button)
        self.setLayout(self.main_layout)

    def update_user_list(self):
        """Update the user present list"""
        self.name_list_widget.clear()
        users = self.controller.get_users_preset_today()
        for user in users:
            self.name_list_widget.addItem(user.user_name)

    def set_face_detection(self, detection: bool):
        self.is_detecting = detection
        if detection is False:
            self.face_thread = None

    def setup_timer(self):
        # Trigger face detection every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.detect_face)
        self.timer.start(1000)

        # Trigger user list update every 2 seconds
        self.sync_attendance_timer = QTimer(self)
        self.sync_attendance_timer.timeout.connect(self.update_user_list)
        self.sync_attendance_timer.start(2000)  # 24 FPS

    def handle_thread(self, user_list):
        print("FOUND USER LIST", user_list)
        for user in user_list:
            self.recognized_face_list.addItem(user)
            QTimer.singleShot(60000, lambda _: self.recognized_face_list.clear())

    def detect_face(self):
        if self.is_detecting is False:
            return
        """Detect and recognize faces in the camera feed."""
        if self.face_thread is None:
            self.face_thread = DetectFaceThread(self.controller)
            self.face_thread.face_detected.connect(self.handle_thread)
            self.face_thread.start()

    def add_name_to_list(self, name: str):
        """Add a recognized name to the list UI."""
        self.name_list_widget.addItem(name)

    def clear_list(self):
        """Clear the list UI."""
        self.name_list_widget.clear()

    def go_back_cb(self, cb):
        self.go_back_button.clicked.connect(cb)
