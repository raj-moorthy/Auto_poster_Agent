import os
from dotenv import load_dotenv

load_dotenv()

# App dirs
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
LOGO_PATH = os.getenv("LOGO_PATH", "logo.png")
SCHEDULE_CHECK_INTERVAL = int(os.getenv("SCHEDULE_CHECK_INTERVAL", "20"))

# Meta (Facebook / Instagram)
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")
META_PAGE_ID = os.getenv("META_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Twitter (X)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
