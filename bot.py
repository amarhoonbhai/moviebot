from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, FORCE_SUB_CHANNEL, TMDB_API_KEY, SUPPORT_CHANNEL, GC_LINK
from parser import parse_movie_data
from database import db
from tmdb_helper import get_movie_details
from ui_templates import format_movie_card, format_leaderboard, format_quiz, format_start, format_guide, format_top_searches, format_stats, format_help, format_about
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

async def show_loading_animation(message: Message) -> Message:
    """Shows a 3-second loading animation."""
    frames = ["🎬 Loading", "🎬 Loading.", "🎬 Loading..", "🎬 Loading..."]
    load_msg = await message.reply_text(frames[0])
    for _ in range(2):
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
    media = message.video or message.document
    if not media: return

    text_to_parse = message.caption or media.file_name or "Unknown Movie"
    data = parse_movie_data(text_to_parse)
    if not data: return

    ext = media.file_name.split('.')[-1] if media.file_name else "mkv"
    year_str = f"({data['year']})" if data['year'] else ""
    clean_name = f"{data['movie_name'].upper()} {year_str} {data['quality']}.{ext}".replace("  ", " ")

    if media.file_name != clean_name:
        logger.info(f"Renaming: {media.file_name} -> {clean_name}")
        path = await message.download(file_name=clean_name)
        caption = f"✅ Auto-Renamed\n🎬 **{data['movie_name']}**"
        try:
            if message.video:
                new_msg = await client.send_video(CHANNEL_ID, video=path, caption=caption, file_name=clean_name)
            else:
                new_msg = await client.send_document(CHANNEL_ID, document=path, caption=caption, file_name=clean_name)
            
            media = new_msg.video or new_msg.document
            msg_id = new_msg.id
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
    
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    last_name = message.from_user.last_name or ""
    
    await db.add_user(user_id, first_name, last_name)
    
    users = await db.get_total_users()
    files = await db.get_total_files()
    
    buttons = [
        [
            InlineKeyboardButton("Search Movie", switch_inline_query_current_chat=""),
            InlineKeyboardButton("Leaderboard", callback_data="show_lb")
        ],
        [
            InlineKeyboardButton("Help Center", callback_data="show_help"),
            InlineKeyboardButton("About Bot", callback_data="show_about")
        ],
        [
            InlineKeyboardButton("Support Channel", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("Group Chat", url=GC_LINK)
        ]
    ]
    
    await message.reply_text(
        format_start(first_name, users, files),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_message(filters.command("guide") & filters.private)
async def guide_cmd(client, message: Message):
    await message.reply_text(format_guide())

@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message: Message):
    await message.reply_text(format_help())

@bot.on_message(filters.command("about") & filters.private)
async def about_cmd(client, message: Message):
    await message.reply_text(format_about())

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
        text = f"⚠️ <b>ACCESS DENIED</b>\n━━━━━━━━━━━━━━━━━━━━\nJoin {FORCE_SUB_CHANNEL} to use the search feature and download files.\n━━━━━━━━━━━━━━━━━━━━"
        btn = [
            [InlineKeyboardButton("📢 Join Channel", url=invite_link)],
            [InlineKeyboardButton("✅ Verify Subscription", callback_data=f"verify_sub_{query if 'query' in locals() else ''}")]
        ]
        return await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/search movie_name`")

    query = " ".join(message.command[1:])
    await db.track_search(query)
    await db.update_points(user_id, 1) # +1 Gem for search

    load_msg = await show_loading_animation(message)
    
    results = await db.search_movies(query)
    if not results:
        await db.save_request(query, user_id)
        await load_msg.edit_text("😔 Movie not found! Request added.")
        return

    first_key = list(results.keys())[0]
    metadata = await get_movie_details(results[first_key]['movie_name'], results[first_key]['year'])
    
    data = results[first_key]
    movie_name = metadata['title'].upper() if metadata else data['movie_name'].upper()
    year = metadata['year'] if metadata else data['year']
    rating = metadata['rating'] if metadata else "7.5"
    language = data["files"][0]["language"]

    text = format_movie_card(movie_name, year, rating, language)
    
    buttons = []
    row = []
    for file in data["files"]:
        quality = file.get('quality') or "Download"
        if not quality or quality.lower() == "unknown": quality = "Download"
        row.append(InlineKeyboardButton(quality, callback_data=f"dl_{file['db_id']}"))
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
    db_id = callback.data.split("_")[1]
    file_data = await db.get_file_by_db_id(db_id)
    if not file_data: return await callback.answer("❌ File not found.")

    await callback.answer("Sending file... 🚀")
    await db.update_points(callback.from_user.id, 2) # +2 Gems for download

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
    global CURRENT_QUIZ
    if not CURRENT_QUIZ or CURRENT_QUIZ.get("answered"):
        return await callback.answer("❌ Quiz ended or already won.")

    ans = int(callback.data.split("_")[1])
    if ans == CURRENT_QUIZ["answer"]:
        CURRENT_QUIZ["answered"] = True
        await db.update_points(callback.from_user.id, 5) # +5 Gems for quiz
        await callback.answer("✅ Correct! +5 Gems added.", show_alert=True)
        await callback.message.edit_text(f"🏆 {callback.from_user.first_name} won the quiz!\nAnswer: {ans}")
    else:
        await callback.answer("❌ Wrong answer! Try again.", show_alert=True)

@bot.on_callback_query(filters.regex(r'^show_'))
async def start_ui_callbacks(client, callback: CallbackQuery):
    data = callback.data.split("_")[1]
    
    if data == "lb":
        users = await db.get_leaderboard()
        await callback.message.edit_text(format_leaderboard(users), reply_markup=callback.message.reply_markup)
    elif data == "guide":
        await callback.message.edit_text(format_guide(), reply_markup=callback.message.reply_markup)
    elif data == "help":
        await callback.message.edit_text(format_help(), reply_markup=callback.message.reply_markup)
    elif data == "about":
        await callback.message.edit_text(format_about(), reply_markup=callback.message.reply_markup)
    elif data == "top":
        searches = await db.get_top_searches()
        await callback.message.edit_text(format_top_searches(searches), reply_markup=callback.message.reply_markup)
    
    await callback.answer()

@bot.on_callback_query(filters.regex(r'^verify_sub_'))
async def verify_sub_handler(client, callback: CallbackQuery):
    """Re-checks subscription status."""
    user_id = callback.from_user.id
    if await is_subscribed(client, user_id):
        await callback.answer("✅ Success! You are now verified.", show_alert=True)
        await callback.message.delete()
        # Optionally re-trigger search if query was passed
        query = callback.data.replace("verify_sub_", "")
        if query:
            # We can't easily re-trigger the message handler, but we can tell them to search again
            await callback.message.reply_text(f"✅ Verified! Please send your search again: <code>/search {query}</code>")
    else:
        await callback.answer("❌ Still not joined! Please join the channel first.", show_alert=True)

# --- ADMIN ---

@bot.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def stats_cmd(client, message: Message):
    users = await db.get_total_users()
    files = await db.get_total_files()
    searches = await db.get_total_search_count()
    points = await db.get_total_points()
    
    lb = await db.get_leaderboard(limit=1)
    top_user_data = lb[0] if lb else {}
    top_user = f"{top_user_data.get('first_name', 'User')} ({top_user_data.get('points', 0)} gems)" if lb else "None"
    
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
    """Sends a math quiz message with 30s timeout."""
    if is_night_mode(): return
    
    n1 = random.randint(1, 100)
    n2 = random.randint(1, 100)
    answer = n1 + n2
    
    options = [answer, answer + random.randint(1, 10), answer - random.randint(1, 10), answer + random.randint(11, 20)]
    random.shuffle(options)
    
    global CURRENT_QUIZ
    
    text = format_quiz(f"{n1} + {n2}", options)
    buttons = [[InlineKeyboardButton(str(opt), callback_data=f"qz_{opt}") for opt in options]]
    
    msg = await bot.send_message(CHANNEL_ID, text, reply_markup=InlineKeyboardMarkup(buttons))
    CURRENT_QUIZ = {"answer": answer, "answered": False, "message_id": msg.id}
    
    await asyncio.sleep(30)
    if not CURRENT_QUIZ.get("answered"):
        try:
            await msg.delete()
        except: pass
    CURRENT_QUIZ = {}

# --- STARTUP ---

async def main():
    if not bot.is_connected:
        await bot.start()
    
    logger.info("Bot started!")
    
    scheduler.add_job(send_math_quiz, "interval", minutes=20)
    scheduler.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
