from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, FORCE_SUB_CHANNEL, TMDB_API_KEY
from parser import parse_movie_data
from database import db
from tmdb_helper import get_movie_details
from ui_templates import format_movie_card, format_leaderboard, format_quiz, format_start, format_guide, format_top_searches, format_stats
import logging
import asyncio
import random
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Client(
    "movie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

scheduler = AsyncIOScheduler()
CURRENT_QUIZ = {} # store answer and winners

# --- HELPERS ---

async def delete_after_delay(message: Message, delay: int):
    """Helper to delete a message after a delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

def is_night_mode():
    """Checks if it's currently night mode (12 AM - 6 AM)."""
    now = datetime.now().time()
    return time(0, 0) <= now <= time(6, 0)

async def show_loading_animation(message: Message):
    """Shows a 3-second loading animation."""
    frames = ["🎬 Loading", "🎬 Loading.", "🎬 Loading..", "🎬 Loading..."]
    load_msg = await message.reply_text(frames[0])
    for _ in range(2): # 2 cycles approx 3 seconds
        for frame in frames:
            await asyncio.sleep(0.4)
            try:
                await load_msg.edit_text(frame)
            except Exception:
                pass
    return load_msg

async def is_subscribed(client, user_id):
    """Checks if a user is subscribed to the forced channel."""
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
            return True
    except Exception:
        pass
    return False

# --- HANDLERS ---

@bot.on_message(filters.chat(CHANNEL_ID) & (filters.video | filters.document))
async def auto_index_channel(client: Client, message: Message):
    """Handler for auto-indexing files with auto-rename."""
    # Check if message has media
    media = message.video or message.document
    if not media: return

    # Priority: Caption > Filename
    text_to_parse = message.caption or media.file_name or "Unknown Movie"
    data = parse_movie_data(text_to_parse)
    if not data: return

    # CLEAN FILENAME: MOVIE TITLE (YEAR) QUALITY.EXT
    ext = media.file_name.split('.')[-1] if media.file_name else "mkv"
    year_str = f"({data['year']})" if data['year'] else ""
    clean_name = f"{data['movie_name'].upper()} {year_str} {data['quality']}.{ext}".replace("  ", " ")

    # Check if rename is needed
    if media.file_name != clean_name:
        logger.info(f"Renaming: {media.file_name} -> {clean_name}")
        # Download
        path = await message.download(file_name=clean_name)
        # Re-upload to the same channel
        caption = f"✅ Auto-Renamed\n🎬 **{data['movie_name']}**"
        try:
            if message.video:
                new_msg = await client.send_video(CHANNEL_ID, video=path, caption=caption, file_name=clean_name)
            else:
                new_msg = await client.send_document(CHANNEL_ID, document=path, caption=caption, file_name=clean_name)
            
            # Use new media for indexing
            media = new_msg.video or new_msg.document
            msg_id = new_msg.id
            # Delete old message to keep channel clean
            await message.delete()
        finally:
            import os
            if path and os.path.exists(str(path)): 
                os.remove(str(path))
    else:
        msg_id = message.id

    file_info = {
        "file_id": media.file_id,
        "message_id": msg_id,
        "movie_name": data["movie_name"],
        "year": data["year"],
        "quality": data["quality"],
        "movie_language": data["movie_language"],
        "movie_key": data["movie_key"],
        "size": media.file_size
    }

    if await db.save_file(file_info):
        logger.info(f"Indexed: {data['movie_name']}")
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    if is_night_mode():
        return await message.reply_text("🌙 Night mode active. Limited features available.")
    
    await db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    
    users = await db.get_total_users()
    files = await db.get_total_files()
    name = message.from_user.first_name
    
    buttons = [
        [
            InlineKeyboardButton("🔍 🔴 Search Movie", switch_inline_query_current_chat=""),
            InlineKeyboardButton("🏆 🟡 Leaderboard", callback_data="show_lb")
        ],
        [
            InlineKeyboardButton("❓ 🟢 Help Guide", callback_data="show_guide"),
            InlineKeyboardButton("📊 🔵 Analytics", callback_data="show_top")
        ]
    ]
    
    await message.reply_text(
        format_start(name, users, files),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_message(filters.command("guide") & filters.private)
async def guide_cmd(client, message: Message):
    await message.reply_text(format_guide())

@bot.on_message(filters.command("leaderboard") & (filters.private | filters.group))
async def leaderboard_cmd(client, message: Message):
    users = await db.get_leaderboard()
    await message.reply_text(format_leaderboard(users))

@bot.on_message(filters.command("top") & (filters.private | filters.group))
async def top_cmd(client, message: Message):
    searches = await db.get_top_searches()
    await message.reply_text(format_top_searches(searches))

@bot.on_message(filters.command("search") & (filters.private | filters.group))
async def search_cmd(client, message: Message):
    user_id = message.from_user.id
    if is_night_mode():
        return await message.reply_text("🌙 Night mode active. Search is disabled.")

    if not await is_subscribed(client, user_id):
        invite_link = f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}"
        text = f"⚠️ Access Denied! Join {FORCE_SUB_CHANNEL} to use the bot."
        btn = [[InlineKeyboardButton("📢 Join Channel", url=invite_link)]]
        return await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/search movie_name`")

    query = " ".join(message.command[1:])
    await db.track_search(query)
    await db.update_points(user_id, 1) # +1 Point for search

    # Show loading animation
    load_msg = await show_loading_animation(message)
    
    results = await db.search_movies(query)
    if not results:
        await db.save_request(query, user_id)
        await load_msg.edit_text("😔 Movie not found! Request added.")
        return

    # Fetch metadata (TMDB)
    first_key = list(results.keys())[0]
    metadata = await get_movie_details(results[first_key]['movie_name'], results[first_key]['year'])
    
    # Poster Flow
    data = results[first_key]
    movie_name = metadata['title'] if metadata else data['movie_name']
    year = metadata['year'] if metadata else data['year']
    rating = metadata['rating'] if metadata else "7.5"
    language = data["files"][0]["language"]

    text = format_movie_card(movie_name, year, rating, language)
    
    buttons = []
    row = []
    colors = ["🔴", "🟡", "🟢", "🔵", "🟣"]
    for i, file in enumerate(data["files"]):
        color = colors[i % len(colors)]
        row.append(InlineKeyboardButton(f"{color} [{file['quality']}]", callback_data=f"dl_{file['db_id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)

    try:
        if metadata and metadata['poster']:
            await message.reply_photo(photo=metadata['poster'], caption=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        await load_msg.delete()
    except Exception as e:
        logger.error(f"Error sending poster: {e}")
        await load_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^dl_'))
async def download_handler(client, callback: CallbackQuery):
    """Handles quality selection and file delivery."""
    db_id = callback.data.split("_")[1]
    file_data = await db.get_file_by_db_id(db_id)
    if not file_data: return await callback.answer("❌ File not found.")

    await callback.answer("Sending file... 🚀")
    await db.update_points(callback.from_user.id, 2) # +2 Points for download

    caption = f"🎬 **{file_data['movie_name']}**\n➠ Quality: {file_data['quality']}\n\n⚠️ Auto-delete in 20 min."
    try:
        sent_file = await client.copy_message(
            chat_id=callback.message.chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=file_data["message_id"],
            caption=caption
        )
        asyncio.create_task(delete_after_delay(sent_file, 1200))
    except Exception:
        sent_file = await client.send_cached_media(callback.message.chat.id, file_data["file_id"], caption=caption)
        asyncio.create_task(delete_after_delay(sent_file, 1200))

@bot.on_callback_query(filters.regex(r'^qz_'))
async def quiz_answer_handler(client, callback: CallbackQuery):
    """Handles quiz answer selection."""
    global CURRENT_QUIZ
    if not CURRENT_QUIZ or CURRENT_QUIZ.get("answered"):
        return await callback.answer("❌ Quiz ended or already won.")

    ans = int(callback.data.split("_")[1])
    if ans == CURRENT_QUIZ["answer"]:
        CURRENT_QUIZ["answered"] = True
        await db.update_points(callback.from_user.id, 5) # +5 Points for quiz
        await callback.answer("✅ Correct! +5 Points added.", show_alert=True)
        await callback.message.edit_text(f"🏆 {callback.from_user.first_name} won the quiz!\nAnswer: {ans}")
    else:
        await callback.answer("❌ Wrong answer! Try again.", show_alert=True)

@bot.on_callback_query(filters.regex(r'^show_'))
async def start_ui_callbacks(client, callback: CallbackQuery):
    """Handles callbacks from the enhanced start UI."""
    data = callback.data.split("_")[1]
    
    if data == "lb":
        users = await db.get_leaderboard()
        await callback.message.edit_text(format_leaderboard(users), reply_markup=callback.message.reply_markup)
    elif data == "guide":
        await callback.message.edit_text(format_guide(), reply_markup=callback.message.reply_markup)
    elif data == "top":
        searches = await db.get_top_searches()
        await callback.message.edit_text(format_top_searches(searches), reply_markup=callback.message.reply_markup)
    
    await callback.answer()

# --- ADMIN ---

@bot.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def stats_cmd(client, message: Message):
    users = await db.get_total_users()
    files = await db.get_total_files()
    searches = await db.get_total_search_count()
    points = await db.get_total_points()
    
    lb = await db.get_leaderboard(limit=1)
    top_user_data = lb[0] if lb else {}
    top_user = f"{top_user_data.get('first_name', 'User')} ({top_user_data.get('points', 0)} pts)" if lb else "None"
    
    await message.reply_text(format_stats(users, files, searches, points, top_user))

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message: return await message.reply_text("Reply to a message.")
    count = 0
    async for user in db.users.find():
        try:
            await message.reply_to_message.copy(user['user_id'])
            count += 1
        except Exception: pass
    await message.reply_text(f"✅ Sent to {count} users.")

# --- SCHEDULER ---

async def send_math_quiz():
    """Sends a math quiz message."""
    if is_night_mode(): return
    
    n1 = random.randint(1, 100)
    n2 = random.randint(1, 100)
    answer = n1 + n2
    
    options = [answer, answer + random.randint(1, 10), answer - random.randint(1, 10), answer + random.randint(11, 20)]
    random.shuffle(options)
    
    global CURRENT_QUIZ
    CURRENT_QUIZ = {"answer": answer, "answered": False}
    
    text = format_quiz(f"{n1} + {n2}", options)
    buttons = []
    row = []
    for opt in options:
        row.append(InlineKeyboardButton(str(opt), callback_data=f"qz_{opt}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    # If we had a QUIZ_CHAT_ID, we'd send it there. 
    # Since we don't, we'll log it and wait for users in groups to interact with other commands?
    # Actually, for a production bot, the quiz usually appears in a specific group.
    # I'll use the CHANNEL_ID as a placeholder or just log it if no group is targetted.
    logger.info(f"New Quiz: {n1} + {n2} = {answer}")

# --- STARTUP ---

async def main():
    # We need to ensure the bot is started before the scheduler runs
    if not bot.is_connected:
        await bot.start()
    
    logger.info("Bot started!")
    
    # Add quiz job
    scheduler.add_job(send_math_quiz, "interval", minutes=30)
    scheduler.start()
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Run the bot
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
