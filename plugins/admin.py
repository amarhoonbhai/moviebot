import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS, CHANNEL_ID
from utils import handle_errors
from database import db
from parser import parse_movie_data
import logging

logger = logging.getLogger(__name__)
DOT = "▪"

@Client.on_message(filters.command("ban") & filters.user(ADMIN_IDS))
@handle_errors
async def ban_cmd(client, message: Message):
    if len(message.command) < 2: return await message.reply_text("Usage: /ban user_id")
    try: await db.ban_user(int(message.command[1]))
    except: pass
    await message.reply_text(f"✅ User {message.command[1]} banned.")

@Client.on_message(filters.command("unban") & filters.user(ADMIN_IDS))
@handle_errors
async def unban_cmd(client, message: Message):
    if len(message.command) < 2: return await message.reply_text("Usage: /unban user_id")
    try: await db.unban_user(int(message.command[1]))
    except: pass
    await message.reply_text(f"✅ User {message.command[1]} unbanned.")

@Client.on_message(filters.command("approve_req") & filters.user(ADMIN_IDS))
@handle_errors
async def approve_req_cmd(client, message: Message):
    if len(message.command) < 3: return await message.reply_text("Usage: /approve_req user_id Movie Name")
    uid = int(message.command[1])
    m_name = " ".join(message.command[2:])
    try:
        await client.send_message(uid, f"✅ <b>Request Approved!</b>\n\nYour requested movie <b>{m_name}</b> has been added to our database.\nTap /search {m_name} to download it now!")
        await message.reply_text(f"✅ Notification sent to {uid}.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to reach user: {e}")

@Client.on_message(filters.command("requests") & filters.user(ADMIN_IDS))
@handle_errors
async def requests_cmd(client, message: Message):
    reqs = await db.get_pending_requests()
    if not reqs:
        return await message.reply_text("✅ <b>No pending requests!</b>")
    
    text = f"📂 <b>PENDING MOVIE REQUESTS</b>\n────────────────────\n"
    for r in reqs:
        text += f"⮩ <code>{r['query'].upper()}</code>\n"
    text += "────────────────────"
    await message.reply_text(text)

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
@handle_errors
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message: return await message.reply_text("❌ Reply to a message.")
    users = await db.get_all_user_ids()
    count = 0
    deleted = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            count += 1
            await asyncio.sleep(0.1)
        except Exception:
            await db.delete_user(uid)
            deleted += 1
    await message.reply_text(f"✅ Sent to {count} users.\n🗑 Deleted {deleted} inactive users.")

@Client.on_message(filters.chat(CHANNEL_ID) & filters.document)
async def index_handler(client, message: Message):
    """Professional Auto-Indexing System."""
    if not message.document: return
    file_unique_id = message.document.file_unique_id
    if not file_unique_id:
        return
    text = message.caption or message.document.file_name
    data = parse_movie_data(text)
    if data:
        data.update({
            "file_id": message.document.file_id,
            "file_unique_id": file_unique_id,
            "message_id": message.id,
            "file_size": message.document.file_size
        })
        await db.save_file(data)

@Client.on_message(filters.document & filters.private & filters.user(ADMIN_IDS))
@handle_errors
async def private_db_upload_handler(client, message: Message):
    """Admin-only instant Private DB Uploader."""
    load_msg = await message.reply_text("⏳ <b>Uploading to Private DB...</b>")
    try:
        copied_msg = await client.copy_message(CHANNEL_ID, message.chat.id, message.id)
        file_unique_id = message.document.file_unique_id
        text = message.caption or message.document.file_name
        data = parse_movie_data(text)
        if data:
            data.update({
                "file_id": message.document.file_id,
                "file_unique_id": file_unique_id,
                "message_id": copied_msg.id,
                "file_size": message.document.file_size
            })
            success = await db.save_file(data)
            if success:
                await load_msg.edit_text(f"✅ <b>Successfully Uploaded & Indexed!</b>\n\n<b>{DOT} Title:</b> <code>{data.get('movie_name')}</code>\n<b>{DOT} Quality:</b> <code>{data.get('quality', 'Unknown')}</code>")
            else:
                await load_msg.edit_text("❌ Database failed to index the file.")
        else:
            await load_msg.edit_text("⚠️ <b>Uploaded to Channel, but Parsing Failed.</b>\nEnsure the filename is formatted correctly.")
    except Exception as e:
        await load_msg.edit_text(f"❌ <b>Upload Failed:</b> {e}")
