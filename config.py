import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Kinolar joylanadigan asosiy kanal (publik yoki private)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./movies.db")