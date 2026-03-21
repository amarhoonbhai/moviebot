from pyrogram import Client, idle
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN
from database import db
from plugins.quiz import send_quiz
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bot with Plugins System
bot = Client(
    "movie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

scheduler = AsyncIOScheduler()

async def main():
    await bot.start()
    
    # Professional Command Menu
    await bot.set_bot_commands([
        BotCommand("start", "➲ Home"),
        BotCommand("search", "➤ Find movies"),
        BotCommand("me", "👤 User Profile"),
        BotCommand("daily", "🎁 Claim Daily Gems"),
        BotCommand("leaderboard", "🏆 Top Performance"),
        BotCommand("top", "🔥 Trending Searches"),
        BotCommand("stats", "📊 Global Statistics"),
        BotCommand("ping", "🚀 Response Latency")
    ])
    
    await db.fix_indexes()
    
    scheduler.add_job(send_quiz, "interval", minutes=20, args=[bot])
    scheduler.start()
    
    logger.info("🔥 v8.0 KERNEL ONLINE | PLUGINS LOADED 🔥")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main())
