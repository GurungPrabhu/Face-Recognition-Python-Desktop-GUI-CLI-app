from PyQt5.QtCore import QThread, pyqtSignal


class DetectFaceThread(QThread):
    face_detected = pyqtSignal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._running = True

    def run(self):
        if not self._running:
            return

        user_list = self.controller.authorize_face()
        self.face_detected.emit(user_list)

    def stop(self):
        self.wait()
        self._running = False
