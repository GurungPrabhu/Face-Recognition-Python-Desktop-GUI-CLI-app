import os
import time
from datetime import datetime
from sklearn.metrics import confusion_matrix, classification_report
from controllers import FaceRegistrationController, FaceRecognitionController
import numpy as np


class FaceRecognitionTester:
    def __init__(self, ctx):
        self.ctx = ctx
        self.y_true = []
        self.y_pred = []
        self.processing_times = []
        self.test_results = []

    def register_user(self, username, image_path):
        """Register a user with their face image"""
        try:
            start_time = time.time()
            controller = FaceRegistrationController(self.ctx)
            face_data = controller.get_embedding(image_path)
            controller.add_user(username, face_data)
            elapsed = time.time() - start_time

            self.test_results.append(
                {
                    "operation": "registration",
                    "username": username,
                    "status": "success",
                    "time": elapsed,
                }
            )
            print(f"✅ Registered {username} in {elapsed:.2f}s")
        except Exception as e:
            self.test_results.append(
                {
                    "operation": "registration",
                    "username": username,
                    "status": "failed",
                    "error": str(e),
                }
            )
            print(f"❌ Failed to register {username}: {str(e)}")

    def detect_face(self, username, image_path):
        """Test face recognition against a known user"""
        try:
            start_time = time.time()
            controller = FaceRecognitionController(self.ctx)
            users = controller.detect_user_by_face(image_path)
            elapsed = time.time() - start_time

            predicted_name = users[0] if users else "Unknown"
            is_match = predicted_name in username

            self.y_true.append(username)
            self.y_pred.append(predicted_name)
            self.processing_times.append(elapsed)

            self.test_results.append(
                {
                    "operation": "recognition",
                    "username": username,
                    "predicted": predicted_name,
                    "is_match": is_match,
                    "time": elapsed,
                }
            )

            if is_match:
                print(f"✅ Correct: {username} recognized in {elapsed:.2f}s")
            else:
                print(f"❌ Incorrect: {username} recognized as {predicted_name}")

        except Exception as e:
            self.test_results.append(
                {
                    "operation": "recognition",
                    "username": username,
                    "status": "failed",
                    "error": str(e),
                }
            )
            print(f"⚠️ Error processing {username}: {str(e)}")

    def evaluate_performance(self):
        """Generate comprehensive performance metrics"""
        import matplotlib.pyplot as plt

        print("\n=== Performance Evaluation ===")

        # Accuracy metrics
        if self.y_true and self.y_pred:
            print("\nConfusion Matrix:")
            labels = sorted(list(set(self.y_true + self.y_pred)))
            cm = confusion_matrix(self.y_true, self.y_pred, labels=labels)
            print(cm)

            # Display confusion matrix using matplotlib
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
            ax.figure.colorbar(im, ax=ax)
            ax.set(
                xticks=np.arange(len(labels)),
                yticks=np.arange(len(labels)),
                xticklabels=labels,
                yticklabels=labels,
                ylabel="True label",
                xlabel="Predicted label",
                title="Confusion Matrix",
            )

            plt.setp(
                ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
            )

            # Annotate cells
            fmt = "d"
            thresh = cm.max() / 2.0
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(
                        j,
                        i,
                        format(cm[i, j], fmt),
                        ha="center",
                        va="center",
                        color="white" if cm[i, j] > thresh else "black",
                    )
            plt.tight_layout()
            plt.show()

            print("\nClassification Report:")
            print(classification_report(self.y_true, self.y_pred))

        success_rate = (
            sum(1 for r in self.test_results if r.get("is_match", False))
            / len(self.y_true)
            if self.y_true
            else 0
        )
        print(f"\nSuccess Rate: {success_rate:.2%}")

    def run_tests(self, test_mode="both"):
        """Run comprehensive tests"""
        test_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_images"
        )

        if test_mode in ["register", "both"]:
            print("\n=== Registering Test Users ===")
            reg_dir = os.path.join(test_dir, "registration")
            for file in os.listdir(reg_dir):
                if file.endswith((".jpg", ".jpeg", ".png")):
                    username = os.path.splitext(file)[0]
                    username = username.split("_")[0]
                    self.register_user(username, os.path.join(reg_dir, file))

        if test_mode in ["test", "both"]:
            print("\n=== Testing Recognition ===")
            test_dir = os.path.join(test_dir, "test")
            for file in os.listdir(test_dir):
                if file.endswith((".jpg", ".jpeg", ".png")):
                    username = os.path.splitext(file)[0]
                    username = username.split("_")[0]
                    self.detect_face(username, os.path.join(test_dir, file))

        self.evaluate_performance()

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"test_reports/test_results_{timestamp}.txt", "w") as f:
            for result in self.test_results:
                f.write(f"{result}\n")
