import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "20000"))