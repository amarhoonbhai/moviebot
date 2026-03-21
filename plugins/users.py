from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils import handle_errors, get_nav_markup
from database import db
from ui_templates import format_start, format_help, format_about, format_profile, format_leaderboard, format_top_searches, format_stats, format_daily

from bson import ObjectId
from config import CHANNEL_ID
from utils import delete_msg
import asyncio

def get_dashboard_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profile", callback_data="dash_profile"), InlineKeyboardButton("📊 Global Stats", callback_data="dash_stats")],
        [InlineKeyboardButton("🎁 Daily Gems", callback_data="dash_daily"), InlineKeyboardButton("🏆 Leaderboard", callback_data="nav_leaderboard")],
        [InlineKeyboardButton("❌ Close", callback_data="dash_close")]
    ])

@Client.on_message(filters.command("start") & filters.private)
@handle_errors
async def start_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].startswith("dl_"):
        db_id = message.command[1].replace("dl_", "")
        file = await db.files.find_one({"_id": ObjectId(db_id)})
        if file:
            await db.update_user_stats(message.from_user.id, points=2, download=True)
            cap = f"🎬 **{file['movie_name']}**\n➠ Quality: {file['quality']}\n\n⚠️ Auto-delete in 20 min."
            msg = await client.copy_message(message.chat.id, CHANNEL_ID, file["message_id"], caption=cap)
            asyncio.create_task(delete_msg(msg, 1200))
            return

    s = await db.get_total_stats()
    text = format_start(s.get('users', 0), s.get('files', 0), message.from_user.first_name)
    await message.reply_text(text, reply_markup=get_nav_markup())

@Client.on_message(filters.command("help") & filters.private)
@handle_errors
async def help_cmd(client, message: Message):
    await message.reply_text(format_help(), reply_markup=get_nav_markup())

@Client.on_message(filters.command("about") & filters.private)
@handle_errors
async def about_cmd(client, message: Message):
    await message.reply_text(format_about())

@Client.on_message(filters.command("me") & filters.private)
@handle_errors
async def me_cmd(client, message: Message):
    profile = await db.get_user_profile(message.from_user.id)
    if not profile: return
    
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "Unknown"
    
    caption_text = format_profile(full_name, profile)
    await message.reply_text(caption_text, reply_markup=get_dashboard_markup())

@Client.on_callback_query(filters.regex(r'^dash_'))
@handle_errors
async def dash_handler(client, callback: CallbackQuery):
    action = callback.data.split("_")[1]
    
    if action == "close":
        return await callback.message.delete()
        
    elif action == "profile":
        profile = await db.get_user_profile(callback.from_user.id)
        name = callback.from_user.first_name or "Unknown"
        text = format_profile(name, profile)
        try: await callback.message.edit_text(text, reply_markup=get_dashboard_markup())
        except: pass
        
    elif action == "stats":
        s = await db.get_total_stats()
        text = format_stats(s)
        try: await callback.message.edit_text(text, reply_markup=get_dashboard_markup())
        except: pass
        
    elif action == "daily":
        success, new_total = await db.claim_daily(callback.from_user.id)
        if success:
            text = format_daily(2, new_total)
        else:
            text = "❌ You have already claimed your daily gems today!\n\n<i>Come back in 24 hours.</i>"
        try: await callback.message.edit_text(text, reply_markup=get_dashboard_markup())
        except: pass
        
    await callback.answer()

@Client.on_message(filters.command("daily") & (filters.private | filters.group))
@handle_errors
async def daily_cmd(client, message: Message):
    success, new_total = await db.claim_daily(message.from_user.id)
    if success:
        await message.reply_text(format_daily(2, new_total))
    else:
        await message.reply_text("❌ You have already claimed your daily reward today. Come back later!")

@Client.on_message(filters.command("leaderboard") & (filters.private | filters.group))
@handle_errors
async def lb_cmd(client, message: Message):
    users = await db.get_leaderboard()
    caption_text = format_leaderboard(users)
    await message.reply_text(caption_text, reply_markup=get_nav_markup())

@Client.on_message(filters.command("id") & (filters.private | filters.group))
@handle_errors
async def id_cmd(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = (f"🆔 <b>IDENTIFICATION</b>\n────────────────────\n"
            f"🔹 <b>User ID</b>: <code>{user_id}</code>\n"
            f"🔹 <b>Chat ID</b>: <code>{chat_id}</code>\n────────────────────")
    await message.reply_text(text)

@Client.on_message(filters.command("top") & (filters.private | filters.group))
@handle_errors
async def top_cmd(client, message: Message):
    searches = await db.get_top_searches()
    caption_text = format_top_searches(searches)
    await message.reply_text(caption_text, reply_markup=get_nav_markup())

@Client.on_message(filters.command("stats") & (filters.private | filters.group))
@handle_errors
async def stats_cmd(client, message: Message):
    s = await db.get_total_stats()
    caption_text = format_stats(s)
    await message.reply_text(caption_text, reply_markup=get_nav_markup())

from datetime import datetime
@Client.on_message(filters.command("ping") & (filters.private | filters.group))
@handle_errors
async def ping_cmd(client, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🔹 <i>Pinging...</i>")
    end = datetime.now()
    delta = (end - start).microseconds / 1000
    await msg.edit_text(f"🚀 <b>PONG!</b>\n────────────────────\n⮩ <code>{delta}ms</code> response")

# Shared Callbacks for navigation
@Client.on_callback_query(filters.regex(r'^help$'))
@handle_errors
async def help_cb_handler(client, callback: CallbackQuery):
    await callback.message.edit_text(format_help(), reply_markup=get_nav_markup())

@Client.on_callback_query(filters.regex(r'^start$'))
@handle_errors
async def start_cb_handler(client, callback: CallbackQuery):
    s = await db.get_total_stats()
    text = format_start(s.get('users', 0), s.get('files', 0), callback.from_user.first_name)
    await callback.message.edit_text(text, reply_markup=get_nav_markup())

@Client.on_callback_query(filters.regex(r'^nav_leaderboard$'))
@handle_errors
async def nav_lb_handler(client, callback: CallbackQuery):
    users = await db.get_leaderboard()
    caption_text = format_leaderboard(users)
    try: await callback.message.edit_text(caption_text, reply_markup=get_nav_markup())
    except: pass
    await callback.answer()

@Client.on_callback_query(filters.regex(r'^nav_quiz$'))
@handle_errors
async def nav_quiz_handler(client, callback: CallbackQuery):
    await callback.answer("Quizzes run automatically every 20 minutes! Watch the group.", show_alert=True)

@Client.on_callback_query(filters.regex(r'^nav_search$'))
@handle_errors
async def nav_search_handler(client, callback: CallbackQuery):
    await callback.answer("Type /search [movie name] to search!", show_alert=True)
