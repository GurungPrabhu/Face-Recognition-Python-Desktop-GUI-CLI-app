from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QSizePolicy,
)
from PyQt5.QtCore import Qt

from controllers import FaceRegistrationController


class RegistrationFormWidget(QWidget):
    def __init__(self, parent=None, ctx=None):
        super().__init__(parent)
        self.ctx = ctx
        self.setup_ui()
        self.embedding = None

        self.controller = FaceRegistrationController(ctx=self.ctx)

    def setup_ui(self):
        """Setup the UI for the Registration Form page"""
        self.name_input = QLineEdit()

        self.scan_button = QPushButton("Scan Face")
        self.scan_button.setStyleSheet("border: 1px solid white; padding: 10px;")

        self.submit_button = QPushButton("Register")
        self.submit_button.setStyleSheet("margin-top: 20px; padding: 10px;")

        self.submit_button.setStyleSheet("background-color: green; color: white;")
        self.scan_button.clicked.connect(self.handle_scan)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.handle_go_back)
        self.back_button.setStyleSheet("margin-top: 20px; padding: 10px; ")

        self.setStyleSheet(
            """
            background-color: transparent;
            """
        )
        form_layout = QFormLayout()
        self.name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Name:", self.name_input)

        layout = QVBoxLayout()
        registration_label = QLabel("Registration Form")
        registration_label.setStyleSheet(
            """
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                }
            """
        )
        registration_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(registration_label)

        # Adjust the size of the form layout and name input
        self.name_input.setFixedHeight(30)
        form_layout.setSpacing(30)
        layout.addLayout(form_layout)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.back_button)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        self.submit_button.clicked.connect(self.handle_submit)

    def handle_go_back(self):
        self.go_back_cb()
        self.reset_form()

    def reset_form(self):
        self.name_input.clear()
        self.embedding = None
        self.scan_button.setText("Scan Face")
        self.scan_button.setStyleSheet("border: 1px solid white; padding: 10px;")

    def handle_submit(self):
        """Handle the submission of the user sign-up form"""
        name = self.name_input.text().strip()
        # Validation start
        if not name:
            self.name_input.setStyleSheet("border: 1px solid red;")
            self.name_input.setPlaceholderText("Required")
            return

        if self.embedding is None:
            self.scan_button.setStyleSheet("border: 1px solid red;")
            self.scan_button.setText("Please scan your face first")
            return
        # Validation end

        if self.controller and self.embedding is not None:
            try:
                self.controller.add_user(name, self.embedding)
            except Exception as e:
                self.scan_button.setStyleSheet("border: 1px solid red;")
                self.scan_button.setText(f"Error: {str(e)}")
                return
            self.submit_cb()
            self.reset_form()

    def register_submit_cb(self, callback):
        """Register the callback for the submit button"""
        self.submit_cb = callback

    def handle_scan(self):
        """Get face embedding from the camera feed"""

        embedding = self.controller.get_embedding()
        self.embedding = embedding
        if self.embedding is not None:
            self.scan_button.setStyleSheet(
                "background-color: rgba(0, 255, 0, 128); color: white; padding: 10px;"
            )
            self.scan_button.setText("Face scan completed")
        pass

    def handle_go_back_cb(self, cb):
        """Register the callback for the Back button"""
        self.go_back_cb = cb
