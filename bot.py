from pyrogram import Client, filters, enums
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
        asyncio.create_task(delete_after_delay(status_msg, 10))
    else:
        logger.info(f"Skipped (Duplicate): {data['movie_name']} ({data['quality']})")

async def delete_after_delay(message: Message, delay: int):
    """Helper to delete a message after a delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

@bot.on_message(filters.command("start") & (filters.private | filters.group))
async def start_cmd(client, message: Message):
    """Handler for the /start command."""
    await db.add_user(message.from_user.id)
    text = (
        "👋 **Welcome to Movie Bot Indexer!**\n\n"
        "I can help you find movies/files indexed from our private channel.\n\n"
        "🔍 **How to use:**\n"
        "Type `/search <movie name>` to find files.\n"
        "Type `/top` to see trending searches."
    )
    sent_msg = await message.reply_text(text)
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        asyncio.create_task(delete_after_delay(sent_msg, 60))
        asyncio.create_task(delete_after_delay(message, 60))

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

@bot.on_message(filters.command("top") & (filters.private | filters.group))
async def top_cmd(client, message: Message):
    """Show trending movies."""
    top_movies = await db.get_top_movies()
    if not top_movies:
        return await message.reply_text("🔥 No trending movies yet!")
    
    text = "🔥 **Trending Movies**\n\n"
    for i, movie in enumerate(top_movies, 1):
        year_str = f"({movie['year']})" if movie['year'] else ""
        text += f"{i}. **{movie['movie_name']} {year_str}** — `{movie['total_searches']} downloads`\n"
    
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        text += "\n🗑️ _This message will be deleted in 60s._"
    
    sent_msg = await message.reply_text(text)
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        asyncio.create_task(delete_after_delay(sent_msg, 60))
        asyncio.create_task(delete_after_delay(message, 60))

@bot.on_message(filters.command("search") & (filters.private | filters.group))
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

    is_group = message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]
    
    for key, data in results.items():
        year_str = f"({data['year']})" if data['year'] else ""
        text = f"🎬 **{data['movie_name']} {year_str}**\n\n"
        text += "Select quality to download:"
        if is_group:
            text += "\n\n🗑️ _This message will be deleted in 60s._"
        
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
            
        sent_msg = await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        if is_group:
            asyncio.create_task(delete_after_delay(sent_msg, 60))
            asyncio.create_task(delete_after_delay(message, 60))

@bot.on_callback_query(filters.regex(r'^dl_'))
async def download_handler(client, callback: CallbackQuery):
    """Handles quality button clicks with tracking and copy_message."""
    db_id = callback.data.split("_")[1]
    file_data = await db.get_file_by_db_id(db_id)
    
    if not file_data:
        return await callback.answer("❌ File not found in database.", show_alert=True)
    
    await callback.answer("Fetching file... 🚀")
    
    # Increment search/download count
    await db.increment_search(file_data["movie_key"])
    
    # Target chat: PM or Group
    target_chat = callback.message.chat.id
    
    caption = (
        f"🎬 **{file_data['movie_name']}**\n"
        f"💿 Quality: {file_data['quality']}\n"
        f"🌐 Language: {file_data['movie_language']}\n\n"
        f"✅ Tag: #{file_data['movie_key'].replace(' ', '_')}\n"
        "⚠️ **Note: This file will be auto-deleted in 20 minutes.**"
    )

    try:
        sent_file = await client.copy_message(
            chat_id=target_chat,
            from_chat_id=CHANNEL_ID,
            message_id=file_data["message_id"],
            caption=caption
        )
        # Schedule auto-delete after 20 minutes (1200 seconds)
        asyncio.create_task(delete_after_delay(sent_file, 1200))
        
    except Exception as e:
        logger.error(f"Error copying message: {e}")
        # Fallback to cached media
        sent_file = await client.send_cached_media(
            chat_id=target_chat,
            file_id=file_data["file_id"],
            caption=caption
        )
        asyncio.create_task(delete_after_delay(sent_file, 1200))

if __name__ == "__main__":
    bot.run()
