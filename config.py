import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "movie_bot")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002363198816"))
# Admin IDs (comma-separated list)
ADMIN_IDS = [int(i.strip()) for i in os.environ.get("ADMIN_IDS", "5459345700").split(",") if i.strip()]
# Force Subscription Channel
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "@philobots")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "https://t.me/philobots")
GC_LINK = os.environ.get("GC_LINK", "https://t.me/Waifu_Grabber_Bots")
