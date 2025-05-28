from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QPushButton,
)
from PyQt5.QtCore import Qt


class MainMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()

    def build_ui(self):
        """Main method to build the UI with both buttons"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        # Build main buttons
        self.build_registration_button()
        self.build_attendance_button()
        self.build_exit_button()

        # Center all buttons vertically and horizontally
        button_container = QVBoxLayout()
        button_container.setAlignment(Qt.AlignCenter)
        button_container.setSpacing(10)
        button_container.addWidget(self.register_button, alignment=Qt.AlignCenter)
        button_container.addWidget(self.attendance_button, alignment=Qt.AlignCenter)
        button_container.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        layout.addStretch()
        layout.addLayout(button_container)
        layout.addStretch()

    def build_exit_button(self):
        """Create the exit app button"""
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setFixedSize(180, 40)
        self.exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 120, 0, 180);
                color: white;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 140, 235, 200);
            }
            QPushButton:pressed {
                background-color: rgba(0, 100, 195, 220);
            }
            """
        )
        self.exit_button.clicked.connect(QApplication.instance().quit)

    def build_registration_button(self):
        """Create the registration button"""
        self.register_button = QPushButton("New User Registration", self)
        self.register_button.setFixedSize(180, 40)
        self.register_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 120, 215, 180);
                color: white;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 140, 235, 200);
            }
            QPushButton:pressed {
                background-color: rgba(0, 100, 195, 220);
            }
            """
        )

    def build_attendance_button(self):
        """Create the attendance button"""
        self.attendance_button = QPushButton("Mark Attendance", self)
        self.attendance_button.setFixedSize(180, 40)
        self.attendance_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(50, 205, 50, 180);
                color: white;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(60, 215, 60, 200);
            }
            QPushButton:pressed {
                background-color: rgba(40, 195, 40, 220);
            }
            """
        )

    def set_registration_button_cb(self, callback):
        """Set the callback for the registration button"""
        self.register_button.clicked.connect(callback)

    def set_attendance_button_cb(self, callback):
        """Set the callback for the attendance button"""
        self.attendance_button.clicked.connect(callback)
