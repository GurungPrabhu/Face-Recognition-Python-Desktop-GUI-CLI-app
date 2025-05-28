from core import AppContext, DETECTION_THRESHOLD
from models import UserRepository
from test import FaceRecognitionTester
from controllers import FaceRegistrationController, FaceRecognitionController


from migration import run_migration_table, run_migration_down
from core import TEST_DB_PATH
import os


def migrate(ctx: AppContext):
    run_migration_table(ctx.db.engine)


def cleanup(ctx: AppContext):
    """Cleanup function to close the camera and release resources."""
    if ctx.db:
        ctx.db.close_connection()
    print("INFO: Cleanup completed.")


def compare_image(ctx: AppContext):
    print("\n--- Compare Image ---")
    print("1. Use photo")

    registration_controller = FaceRegistrationController(ctx)
    photo_path_1 = input("Enter the path to the photo: ").strip()
    photo_path_2 = input("Enter the path to the photo: ").strip()
    face_data = registration_controller.get_embedding(photo_path_1)
    face_data_2 = registration_controller.get_embedding(photo_path_2)

    # Test
    recognition_controller = FaceRecognitionController(ctx)

    sim = recognition_controller.f_detector.match_face(
        face_data[0], face_data_2[0], threshold=DETECTION_THRESHOLD
    )

    print("Similarity between two data", sim)


def sign_up(ctx: AppContext):
    print("\n--- Sign Up ---")
    username = input("Enter username: ")
    user_repo = UserRepository(ctx)

    user = user_repo.get_by_name(username)
    if user:
        print("ERROR: Username already exists.")
        return

    print("\n--- Register Face ---")
    print("1. Scan face using camera")
    print("2. Use photo")
    choice = input("Enter choice [1-2]: ").strip()

    registration_controller = FaceRegistrationController(ctx)

    if choice == "1":
        print("INFO: Scanning face using camera...")
        try:
            face_data = registration_controller.get_embedding()
        except Exception as e:
            print("ERROR:", e)
            face_data = None

    elif choice == "2":
        photo_path_1 = input("Enter the path to the photo: ").strip()

        try:
            face_data = registration_controller.get_embedding(photo_path_1)
        except Exception as e:
            print("ERROR:", e)
            face_data = None

    else:
        print("ERROR: Invalid choice. Registration aborted.")
        return

    if not face_data:
        print("ERROR: Face registration failed. Try again.")
        return

    # Register the user
    registration_controller.add_user(username, face_data)
    print("SUCCESS: User registered.")


def sign_in(ctx: AppContext):
    print("\n--- Sign In ---")

    print("\n--- Authenticate Face ---")
    print("1. Scan face using camera")
    print("2. Use photo")
    choice = input("Enter choice [1-2]: ").strip()

    recognition_controller = FaceRecognitionController(ctx)

    if choice == "1":
        print("INFO: Verifying user with face recognition using camera...")
        recognized_users = recognition_controller.authorize_face()

    elif choice == "2":
        photo_path = input("Enter the path to the photo: ").strip()
        print(
            f"INFO: Verifying user with face recognition using photo from {photo_path}..."
        )
        recognized_users = recognition_controller.authorize_face(photo_path)
    else:
        print("ERROR: Invalid choice. Authentication aborted.")
        return

    if len(recognized_users) == 0:
        print("ERROR: No absent user registered. Make sure you are absent. Try again.")
        return

    for user in recognized_users:
        print(f"SUCCESS: User {user} attendance marked.")


def main():
    ctx = AppContext()
    migrate(ctx)

    try:
        while True:
            print("\n=== CLI Menu ===")
            print("1. Sign Up")
            print("2. Mark Attendance")
            print("3. Run Tests")
            print("4. Compare two image for face similarity")
            print("5. Exit")
            choice = input("Enter choice [1-5]: ").strip()

            if choice == "1":
                sign_up(ctx)
            elif choice == "2":
                sign_in(ctx)
            elif choice == "3":
                test_ctx = AppContext(TEST_DB_PATH)
                migrate(test_ctx)
                tester = FaceRecognitionTester(test_ctx)
                tester.run_tests()

                cleanup(test_ctx)

                # Delete the test database
                run_migration_down(test_ctx.db.engine)
            elif choice == "4":
                compare_image(ctx)
                break
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Try again.")

    finally:
        cleanup(ctx)


if __name__ == "__main__":
    main()
