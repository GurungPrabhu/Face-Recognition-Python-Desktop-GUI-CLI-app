import os
import sys
import time
from PyQt5.QtWidgets import QApplication
import cv2

from controllers import FaceRegistrationController
from views import MainPage
from core import AppContext

from migration import run_migration_table


def seed_user_to_db(ctx):
    """Register all test images to the database."""
    try:
        controller = FaceRegistrationController(ctx)
        users = controller.repository.get_all()

        if len(users) > 0:
            print("INFO: Users already registered in the database.")
            return
        # Define the directory for test images
        test_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test_images",
            "registration",
        )

        # Iterate over all images in the test directory
        for file in os.listdir(test_dir):
            if file.endswith((".jpg", ".jpeg", ".png")):
                # Extract the username from the filename
                username = os.path.splitext(file)[0]
                username = username.split("_")[0]

                # Register the user
                image_path = os.path.join(test_dir, file)
                start_time = time.time()
                face_data = controller.get_embedding(image_path)
                try:
                    controller.add_user(username, face_data)
                    elapsed = time.time() - start_time
                except Exception as e:
                    continue

                print(f"✅ Registered {username} in {elapsed:.2f}s")

    except Exception as e:
        print(f"❌ Failed to register test images: {str(e)}")


# Run migration for User and Attendance table
def migrate(ctx: AppContext):
    run_migration_table(ctx.db.engine)


# Cleanup function to close the camera and database connection
def cleanup(ctx: AppContext):
    """Cleanup function to close the camera and release resources."""
    if ctx.db:
        ctx.db.close_connection()
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
    print("INFO: Cleanup completed.")


def main():
    # Global application context
    ctx = AppContext()

    app = QApplication(sys.argv)

    migrate(ctx)
    seed_user_to_db(ctx)

    # Cleanup function to be called on exit
    app.aboutToQuit.connect(lambda: cleanup(ctx))

    window = MainPage(ctx)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
