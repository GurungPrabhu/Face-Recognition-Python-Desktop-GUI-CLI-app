import os

APP_NAME = "AMS"
APP_VERSION = "0.0.1"


# Paths
USER_HOME = os.path.expanduser("~")
DB_NAME = "main.db"
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../database/", DB_NAME
)

TEST_DB_NAME = "test_main.db"
TEST_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../database/", TEST_DB_NAME
)

# UI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Other
DEBUG = True

# Test data
TEST_DATA_LOCATION = "../test_images"

# Detection threshold
DETECTION_THRESHOLD = 0.7
