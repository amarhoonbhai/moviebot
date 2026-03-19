from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_IDS
from parser import parse_movie_data
from database import db
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Client(
    "movie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.chat(CHANNEL_ID) & (filters.video | filters.document))
async def auto_index_channel(client, message: Message):
    """Handler for auto-indexing files from the private channel."""
    # Priority: Caption > Filename
    text_to_parse = message.caption or (message.video.file_name if message.video else message.document.file_name)
    
    if not text_to_parse:
        return

    data = parse_movie_data(text_to_parse)
    if not data:
        return

    file_obj = message.video or message.document
    
    file_info = {
        "file_id": file_obj.file_id,
        "message_id": message.id,
        "movie_name": data["movie_name"],
        "year": data["year"],
        "quality": data["quality"],
        "movie_language": data["movie_language"],
        "movie_key": data["movie_key"],
        "size": file_obj.file_size
    }

    success = await db.save_file(file_info)
    if success:
        logger.info(f"Indexed: {data['movie_name']} ({data['quality']})")
        # Send confirmation and auto-delete
        status_msg = await message.reply_text(
            f"✅ **Successful Indexed:**\n`{data['movie_name']} ({data['year'] or ''}) [{data['quality']}]`"
        )
        await asyncio.sleep(10)
        await status_msg.delete()
    else:
        logger.info(f"Skipped (Duplicate): {data['movie_name']} ({data['quality']})")

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    """Cool welcome message and user tracking."""
    await db.add_user(message.from_user.id)
    welcome_text = (
        "🎬 **Welcome to Movie Bot Indexer!** 🍿\n\n"
        "I can help you find and download files from our private collection.\n\n"
        "🔍 **Commands:**\n"
        "/search <name> - Find movies\n"
        "/top - Show trending movies\n"
        "/help - Show this message\n\n"
        "Example: `/search dark knight`"
    )
    await message.reply_text(welcome_text)

@bot.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def stats_cmd(client, message: Message):
    """Admin stats command."""
    users = await db.get_total_users()
    files = await db.get_total_files()
    text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 **Total Users:** `{users}`\n"
        f"📂 **Total Indexed Files:** `{files}`"
    )
    await message.reply_text(text)

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_cmd(client, message: Message):
    """Admin broadcast command."""
    if not message.reply_to_message:
        return await message.reply_text("❌ Please reply to a message to broadcast.")
    
    msg = await message.reply_text("Sending broadcast... ⏳")
    count = 0
    # In a real production bot, we'd use a more robust way to iterate
    async for user in db.users.find():
        try:
            await message.reply_to_message.copy(user['user_id'])
            count += 1
        except Exception:
            pass
    
    await msg.edit_text(f"✅ Broadcast sent to `{count}` users.")

@bot.on_message(filters.command("top") & filters.private)
async def top_cmd(client, message: Message):
    """Show trending movies."""
    top_movies = await db.get_top_movies()
    if not top_movies:
        return await message.reply_text("🔥 No trending movies yet!")
    
    text = "🔥 **Trending Movies**\n\n"
    for i, movie in enumerate(top_movies, 1):
        year_str = f"({movie['year']})" if movie['year'] else ""
        text += f"{i}. **{movie['movie_name']} {year_str}** — `{movie['total_searches']} downloads`\n"
    
    await message.reply_text(text)

@bot.on_message(filters.command("search") & filters.private)
async def search_cmd(client, message: Message):
    """Search for movies and display grouped results."""
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a movie name to search.\nExample: `/search avengers`")
    
    # Track user
    await db.add_user(message.from_user.id)
    
    query = " ".join(message.command[1:])
    results = await db.search_movies(query)
    
    if not results:
        return await message.reply_text("😔 Sorry, no movies found matching your search.")

    for key, data in results.items():
        year_str = f"({data['year']})" if data['year'] else ""
        text = f"🎬 **{data['movie_name']} {year_str}**\n\n"
        text += "Select quality to download:"
        
        buttons = []
        sorted_files = sorted(data["files"], key=lambda x: x["quality"])
        
        row = []
        for file in sorted_files:
            btn_text = f"[{file['quality']}]"
            row.append(InlineKeyboardButton(btn_text, callback_data=f"dl_{file['db_id']}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
            
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^dl_'))
async def download_handler(client, callback: CallbackQuery):
    """Handles quality button clicks with tracking and copy_message."""
    db_id = callback.data.split("_")[1]
    file_data = await db.get_file_by_db_id(db_id)
    
    if not file_data:
        return await callback.answer("❌ File not found in database.", show_alert=True)
    
    await callback.answer("Fetching file from channel...")
    
    # Increment search/download count
    await db.increment_search(file_data["movie_key"])
    
    # Send the file by copying it from the channel
    # This ensures it's "fetched" from the source correctly
    try:
        await client.copy_message(
            chat_id=callback.from_user.id,
            from_chat_id=CHANNEL_ID,
            message_id=file_data["message_id"],
            caption=f"🎬 **{file_data['movie_name']}**\n💿 Quality: {file_data['quality']}\n🌐 Language: {file_data['movie_language']}\n\n✅ Tag: #{file_data['movie_key'].replace(' ', '_')}"
        )
    except Exception as e:
        logger.error(f"Error copying message: {e}")
        # Fallback to cached media if copy fails (e.g. message deleted)
        await client.send_cached_media(
            chat_id=callback.from_user.id,
            file_id=file_data["file_id"],
            caption=f"🎬 **{file_data['movie_name']}**\n💿 Quality: {file_data['quality']}\n🌐 Language: {file_data['movie_language']}"
        )

if __name__ == "__main__":
    bot.run()
