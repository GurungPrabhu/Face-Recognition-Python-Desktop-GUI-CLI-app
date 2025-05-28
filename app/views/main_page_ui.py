import sys
import cv2
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

from core import APP_NAME
from .widgets import RegistrationFormWidget, RecognitionWidget, MainMenuWidget
from thread import VideoCaptureThread


class MainPage(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.setup_ui()

    # Setup registration menu UI
    def _setup_registration_menu_ui(self):
        registration_widget = RegistrationFormWidget(
            self.button_container, ctx=self.ctx
        )
        registration_widget.register_submit_cb(self.on_click_registration_success)
        registration_widget.handle_go_back_cb(self.load_main_menu)
        return registration_widget

    # Setup Main menu UI
    def _setup_main_menu_ui(self):
        main_menu_widget = MainMenuWidget(self)
        main_menu_widget.set_registration_button_cb(self.on_click_registration)
        main_menu_widget.set_attendance_button_cb(self.on_click_attendance)
        return main_menu_widget

    # Setup Recognition UI
    def _setup_recognition_ui(self):
        recognition_widget = RecognitionWidget(self.button_container, self.ctx)
        recognition_widget.go_back_cb(self.on_click_go_back_recognition)
        return recognition_widget

    # Setup whole UI in main window
    def setup_ui(self):
        # Main window settings
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1024, 768)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main Camera background
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camera_label)

        # Center layout main container
        self.button_container = QWidget(self)
        self.button_container.setStyleSheet("background-color:  rgba(0, 0, 0, 0.5);")
        self.button_container.setFixedSize(310, 300)

        self.button_container_layout = QVBoxLayout()
        self.button_container_layout.setAlignment(Qt.AlignCenter)
        self.button_container_layout.addWidget(self.button_container)

        # Register Widget setup
        self.stacked_widget = QStackedWidget()

        self.recognition_widget = self._setup_recognition_ui()
        main_menu_widget = self._setup_main_menu_ui()
        registration_widget = self._setup_registration_menu_ui()

        self.stacked_widget.addWidget(self.recognition_widget)  # Index 0
        self.stacked_widget.addWidget(registration_widget)  # Index 1
        self.stacked_widget.addWidget(main_menu_widget)  # Index 2

        # Default active menu
        self.stacked_widget.setCurrentIndex(2)

        # Layout for buttons inside container
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.addWidget(self.stacked_widget, alignment=Qt.AlignCenter)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(0)

        self._setup_video_thread()
        self.center_buttons()

    def _setup_video_thread(self):
        # Initialize video capture thread to prevent from blocking the UI
        self.video_thread = VideoCaptureThread(self.ctx)
        self.video_thread.set_detect_user(True)
        self.video_thread.frame_ready.connect(self.update_frame)
        self.video_thread.start()

    def center_buttons(self):
        """Align the main container  on top of the camera feed"""
        if hasattr(self, "button_container") and self.button_container:
            # Calculate center position
            container_width = self.button_container.width()
            container_height = self.button_container.height()
            x = (self.width() - container_width) // 2
            y = (self.height() - container_height) // 2

            self.button_container.move(x, y)

    def on_click_registration(self):
        """Load the registration widget when the button is clicked"""
        self.stacked_widget.setCurrentIndex(1)

    def load_main_menu(self):
        """Load the main menu widget when the button is clicked"""
        self.recognition_widget.set_face_detection(False)
        self.stacked_widget.setCurrentIndex(2)

    def load_recognition_menu(self):
        """Load the attendance widget when the button is clicked"""
        self.recognition_widget.set_face_detection(True)
        self.stacked_widget.setCurrentIndex(0)

    def on_click_registration_success(self):
        self.load_main_menu()

    def on_click_attendance(self):
        self.load_recognition_menu()

    def on_click_go_back_recognition(self):
        self.load_main_menu()

    def update_frame(self, frame):
        # Convert the image from BGR (OpenCV) to RGB (Qt)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # Scale the pixmap to fit the label while maintaining aspect ratio
        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def closeEvent(self, event):
        """Clean up when closing the application"""
        self.timer.stop()
        self.capture.release()
        event.accept()
