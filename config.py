import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "-1001234567890"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./movies.db")
WEB_PASSWORD = os.getenv("WEB_PASSWORD", "admin123")

# For SQLite fallback, replace postgresql with sqlite if DATABASE_URL not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./movies.db"