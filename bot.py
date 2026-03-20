from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, FORCE_SUB_CHANNEL, TMDB_API_KEY, SUPPORT_CHANNEL, GC_LINK, GROUP_ID
from parser import parse_movie_data
from database import db
from tmdb_helper import get_movie_details
from ui_templates import format_movie_card, format_leaderboard, format_quiz, format_start, format_guide, format_top_searches, format_help, format_about, format_profile
import logging
import asyncio
import random
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson import ObjectId

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

# --- HELPERS ---

def handle_errors(func):
    """Professional Error Shield."""
    async def wrapper(client, msg, *args, **kwargs):
        try:
            # 1. Broad User Validation (CRITICAL)
            if not msg.from_user: return
            # 2. Auto-save user to DB (Standardized)
            await db.save_user(msg.from_user)
            return await func(client, msg, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            if "DuplicateKeyError" in str(e):
                await db.fix_indexes() # Self-healing
            try:
                text = "❌ <b>SYSTEM ERROR</b>\n━━━━━━━━━━━━━━━━━━━━\nAn unexpected error occurred. Admin has been notified."
                if isinstance(msg, Message): await msg.reply_text(text)
                elif isinstance(msg, CallbackQuery): await msg.answer("❌ System Error.", show_alert=True)
            except: pass
    return wrapper

async def is_subscribed(client, user_id):
    """Strict membership check."""
    if not FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL.lower() == "none": return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]
    except Exception: return False

async def show_loading(message: Message):
    frames = ["🎬 Loading", "🎬 Loading.", "🎬 Loading..", "🎬 Loading..."]
    load_msg = await message.reply_text(frames[0])
    for _ in range(2):
        for f in frames:
            await asyncio.sleep(0.4)
            try: await load_msg.edit_text(f)
            except: pass
    return load_msg

# --- COMMANDS ---

@bot.on_message(filters.command("start") & filters.private)
@handle_errors
async def start_cmd(client, message: Message):
    await message.reply_text(format_start(0, 0, message.from_user.first_name))

@bot.on_message(filters.command("help") & filters.private)
@handle_errors
async def help_cmd(client, message: Message):
    await message.reply_text(format_help())

@bot.on_message(filters.command("about") & filters.private)
@handle_errors
async def about_cmd(client, message: Message):
    await message.reply_text(format_about())

@bot.on_message(filters.command("me") & filters.private)
@handle_errors
async def me_cmd(client, message: Message):
    profile = await db.get_user_profile(message.from_user.id)
    await message.reply_text(format_profile(profile)) if profile else None

@bot.on_message(filters.command("leaderboard") & (filters.private | filters.group))
@handle_errors
async def lb_cmd(client, message: Message):
    users = await db.get_leaderboard()
    await message.reply_text(format_leaderboard(users))

@bot.on_message(filters.command("top") & (filters.private | filters.group))
@handle_errors
async def top_cmd(client, message: Message):
    searches = await db.get_top_searches()
    await message.reply_text(format_top_searches(searches))

@bot.on_message(filters.command("search") & (filters.private | filters.group))
@handle_errors
async def search_cmd(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/search movie_name`")

    query = " ".join(message.command[1:])
    if not await is_subscribed(client, user_id):
        invite = f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}"
        text = f"⚠️ <b>ACCESS DENIED</b>\n━━━━━━━━━━━━━━━━━━━━\nJoin {FORCE_SUB_CHANNEL} to search and download.\n━━━━━━━━━━━━━━━━━━━━"
        btn = [[InlineKeyboardButton("📢 Join Channel", url=invite)], [InlineKeyboardButton("✅ Verify", callback_data=f"verify_sub_{query}")]]
        return await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

    await db.track_search(query)
    await db.update_user_stats(user_id, points=1, search=True)
    
    load_msg = await show_loading(message)
    results = await db.search_movies(query, limit=10) # Pagination base
    
    if not results:
        await db.save_request(query, user_id)
        return await load_msg.edit_text("😔 Movie not found! Request added to admin queue.")

    # Show first result
    data = results[0]
    metadata = await get_movie_details(data['movie_name'], data['year'])
    
    name = metadata['title'].upper() if metadata else data['movie_name'].upper()
    year = metadata['year'] if metadata else data['year']
    
    buttons = []
    # Quality Buttons
    # In this rebuild, we search files matching the name. 
    # For now, we show the first file. Future: Pagination menu.
    row = []
    for r in results[:5]: # Show top 5 qualities/files for this query
        row.append(InlineKeyboardButton(r.get('quality', 'DL'), callback_data=f"dl_{r['_id']}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)

    text = format_movie_card(name, year, metadata['rating'] if metadata else "N/A", data.get('language', 'Unknown'))
    
    try:
        if metadata and metadata['poster']:
            await message.reply_photo(photo=metadata['poster'], caption=text, reply_markup=InlineKeyboardMarkup(buttons))
        else: await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        await load_msg.delete()
    except Exception:
        await load_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- CALLBACKS ---

@bot.on_callback_query(filters.regex(r'^dl_'))
@handle_errors
async def dl_handler(client, callback: CallbackQuery):
    db_id = callback.data.split("_")[1]
    file = await db.files.find_one({"_id": ObjectId(db_id)})
    if not file: return await callback.answer("❌ File not found.")

    await callback.answer("Sending file... 🚀")
    await db.update_user_stats(callback.from_user.id, points=2, download=True)

    cap = f"🎬 **{file['movie_name']}**\n➠ Quality: {file['quality']}\n\n⚠️ Auto-delete in 20 min."
    # Copy from channel
    msg = await client.copy_message(callback.message.chat.id, CHANNEL_ID, file["message_id"], caption=cap)
    asyncio.create_task(delete_msg(msg, 1200))

@bot.on_callback_query(filters.regex(r'^verify_sub_'))
@handle_errors
async def verify_handler(client, callback: CallbackQuery):
    if await is_subscribed(client, callback.from_user.id):
        await callback.answer("✅ Verified!", show_alert=True)
        await callback.message.delete()
        q = callback.data.replace("verify_sub_", "")
        if q: await callback.message.reply_text(f"✅ Verified! Search again: `/search {q}`")
    else:
        await callback.answer("❌ Still not joined!", show_alert=True)

# --- QUIZ ---

async def send_quiz():
    if time(0, 0) <= datetime.now().time() <= time(6, 0): return
    n1, n2 = random.randint(1, 20), random.randint(1, 20)
    ans = n1 + n2
    opts = random.sample(range(max(1, ans-5), ans+10), 3) + [ans]
    random.shuffle(opts)
    
    await db.create_quiz(f"WHAT IS {n1} + {n2}?", ans, opts)
    text = format_quiz(f"{n1} + {n2}", opts)
    btns = [[InlineKeyboardButton(str(o), callback_data=f"qz_{o}")] for o in opts]
    msg = await bot.send_message(GROUP_ID, text, reply_markup=InlineKeyboardMarkup(btns))
    await asyncio.sleep(30); await msg.delete()

@bot.on_callback_query(filters.regex(r'^qz_'))
@handle_errors
async def qz_handler(client, callback: CallbackQuery):
    quiz = await db.get_active_quiz()
    if not quiz or quiz["answered_by"]: return await callback.answer("❌ Ended.")
    
    ans = int(callback.data.split("_")[1])
    if ans == quiz["correct_answer"]:
        if await db.claim_quiz(quiz["_id"], callback.from_user.id):
            await db.update_user_stats(callback.from_user.id, points=5)
            await callback.answer("✅ WINNER! +5 Gems.", show_alert=True)
            await callback.message.edit_text(f"🏆 {callback.from_user.first_name} won the quiz!\nAnswer: {ans}")
    else: await callback.answer("❌ Wrong!", show_alert=True)

# --- ADMIN ---

@bot.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
@handle_errors
async def stats_cmd(client, message: Message):
    s = await db.get_total_stats()
    text = f"📊 **SYSTEM STATS**\n━━━━━━━━━━━━━━━━━━━━\nUsers: {s['users']}\nFiles: {s['files']}\nSearches: {s['searches']}\n━━━━━━━━━━━━━━━━━━━━"
    await message.reply_text(text)

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
@handle_errors
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message: return await message.reply_text("❌ Reply to a message.")
    users = await db.get_all_user_ids()
    count = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            count += 1
            await asyncio.sleep(0.1)
        except: pass
    await message.reply_text(f"✅ Sent to {count} users.")

# --- STARTUP ---

async def delete_msg(msg, delay):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def main():
    await bot.start()
    await bot.set_bot_commands([
        BotCommand("start", "Home"),
        BotCommand("search", "Find movies"),
        BotCommand("me", "Profile"),
        BotCommand("leaderboard", "Top users"),
        BotCommand("top", "Trending"),
        BotCommand("stats", "Admin stats")
    ])
    await db.fix_indexes()
    scheduler.add_job(send_quiz, "interval", minutes=20)
    scheduler.start()
    logger.info("PRO-BACKEND ACTIVE 🚀")

if __name__ == "__main__":
    bot.run(main())
