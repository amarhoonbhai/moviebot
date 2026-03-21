import asyncio
import logging
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
from config import FORCE_SUB_CHANNEL, GROUP_ID
from database import db

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Professional Error Shield."""
    async def wrapper(client, msg, *args, **kwargs):
        try:
            if not msg.from_user: return
            user_data = await db.users.find_one({"telegram_user_id": msg.from_user.id})
            if user_data and user_data.get("is_banned"):
                if isinstance(msg, Message): await msg.reply_text("❌ You are banned from using this bot.")
                elif isinstance(msg, CallbackQuery): await msg.answer("❌ You are banned.", show_alert=True)
                return
            await db.save_user(msg.from_user)
            
            # --- GLOBAL FORCE SUB CHECK ---
            from config import ADMIN_IDS
            user_id = msg.from_user.id
            if user_id not in ADMIN_IDS:
                is_verify = isinstance(msg, CallbackQuery) and msg.data.startswith("verify_sub")
                if not is_verify:
                    if not await is_subscribed(client, user_id):
                        from config import GC_LINK, FORCE_SUB_CHANNEL
                        invite = f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}"
                        text = f"⚠️ <b>ACCESS DENIED</b>\n━━━━━━━━━━━━━━━━━━━━\nYou must join our Channel & Group to use this bot.\n━━━━━━━━━━━━━━━━━━━━"
                        
                        q = ""
                        if isinstance(msg, Message) and msg.text and msg.text.startswith("/search"):
                            if len(msg.command) > 1: q = " ".join(msg.command[1:])
                            
                        btn = [
                            [InlineKeyboardButton("📢 Join Channel", url=invite), InlineKeyboardButton("💬 Join Group", url=GC_LINK)],
                            [InlineKeyboardButton("✅ Verify", callback_data=f"verify_sub_{q}" if q else "verify_sub_")]
                        ]
                        if isinstance(msg, Message):
                            await msg.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))
                        elif isinstance(msg, CallbackQuery):
                            await msg.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btn))
                        return
            # ------------------------------
            
            return await func(client, msg, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            if "DuplicateKeyError" in str(e):
                await db.fix_indexes()
            try:
                text = "❌ <b>SYSTEM ERROR</b>\n━━━━━━━━━━━━━━━━━━━━\nAn unexpected error occurred. Admin has been notified."
                if isinstance(msg, Message): await msg.reply_text(text)
                elif isinstance(msg, CallbackQuery): await msg.answer("❌ System Error.", show_alert=True)
            except: pass
    return wrapper

async def is_subscribed(client, user_id):
    try:
        # Check Channel
        if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL.lower() != "none":
            ch_member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
            if ch_member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                return False
                
        # Check Group
        if GROUP_ID:
            gc_member = await client.get_chat_member(GROUP_ID, user_id)
            if gc_member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                return False
                
        return True
    except Exception:
        return False

async def show_loading(message: Message):
    frames = ["🎬 Loading", "🎬 Loading.", "🎬 Loading..", "🎬 Loading..."]
    load_msg = await message.reply_text(frames[0])
    for _ in range(2):
        for f in frames:
            await asyncio.sleep(0.4)
            try: await load_msg.edit_text(f)
            except: pass
    return load_msg

def get_nav_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏆 View Leaderboard", callback_data="nav_leaderboard"), InlineKeyboardButton("🎲 Play Quiz", callback_data="nav_quiz")],
        [InlineKeyboardButton("🔍 Search Movie", callback_data="nav_search"), InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

async def delete_msg(msg, delay):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass
