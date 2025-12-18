import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

API_URL = "http://172.27.27.98:8000/api/store-time-tracking"

DEFAULT_USER_ID = 10
DEFAULT_TASK_ID = 1

LOG_DIR = os.path.join(BASE_DIR, "logs")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")

INACTIVITY_THRESHOLD = 60
