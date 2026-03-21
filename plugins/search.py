from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS, FORCE_SUB_CHANNEL, CHANNEL_ID
from utils import handle_errors, is_subscribed, show_loading, get_nav_markup, delete_msg
from database import db
from tmdb_helper import get_movie_details
from ui_templates import format_movie_card
from bson import ObjectId
import asyncio

async def send_search_page(message_or_callback, query, page=0, user_id=None):
    if user_id is None: user_id = message_or_callback.from_user.id
    results = await db.search_movies(query, offset=page*5, limit=6)
    
    if not results and page == 0:
        await db.save_request(query, user_id)
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.answer("😔 Movie not found! Request added to admin queue.", show_alert=True)
        else:
            await message_or_callback.reply_text("😔 Movie not found! Request added to admin queue.")
        return
        
    if not results:
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.answer("No more results.", show_alert=True)
        return

    has_next = len(results) > 5
    page_results = results[:5]
    
    data = page_results[0]
    metadata = await get_movie_details(data['movie_name'], data['year'])
    
    name = metadata['title'].upper() if metadata else data['movie_name'].upper()
    year = metadata['year'] if metadata else data['year']
    
    buttons = []
    row = []
    for r in page_results:
        quality = r.get('quality', 'DL')
        btn_text = quality if quality != "Unknown" else "Download 📥"
        row.append(InlineKeyboardButton(btn_text, callback_data=f"dl_{r['_id']}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)

    if user_id in ADMIN_IDS:
        del_row = []
        for r in page_results:
            quality = r.get('quality', 'DL')
            del_text = f"🗑 Del {quality}" if quality != "Unknown" else "🗑 Del"
            del_row.append(InlineKeyboardButton(del_text, callback_data=f"del_{r['_id']}"))
            if len(del_row) == 2:
                buttons.append(del_row); del_row = []
        if del_row: buttons.append(del_row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"spg_{page-1}_{query[:30]}"))
    if has_next:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"spg_{page+1}_{query[:30]}"))
    if nav_row: buttons.append(nav_row)

    lang = data.get('language', 'Multi')
    if lang == "Unknown": lang = "Multi"
    
    runtime = metadata.get('runtime', 'N/A') if metadata else 'N/A'
    genres = metadata.get('genres', 'N/A') if metadata else 'N/A'
    director = metadata.get('director', 'Unknown') if metadata else 'Unknown'
    cast = metadata.get('cast', 'Unknown') if metadata else 'Unknown'
    plot = metadata.get('plot', 'No plot available') if metadata else ''
    
    text = format_movie_card(name, year, metadata['rating'] if metadata else "N/A", lang, runtime, genres, director, cast, plot, metadata.get('seasons') if metadata else None)
    
    if isinstance(message_or_callback, CallbackQuery):
        try:
            await message_or_callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            try:
                if metadata and metadata['poster']:
                    await message_or_callback.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons))
            except: pass
    else:
        try:
            if metadata and metadata['poster']:
                await message_or_callback.reply_photo(photo=metadata['poster'], caption=text, reply_markup=InlineKeyboardMarkup(buttons))
            else: await message_or_callback.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            await message_or_callback.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("search") & (filters.private | filters.group))
@handle_errors
async def search_cmd(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/search movie_name`")

    query = " ".join(message.command[1:])

    await db.track_search(query)
    await db.update_user_stats(user_id, points=1, search=True)
    
    load_msg = await show_loading(message)
    await send_search_page(message, query, page=0, user_id=user_id)
    try: await load_msg.delete()
    except: pass

@Client.on_callback_query(filters.regex(r'^verify_sub_'))
@handle_errors
async def verify_handler(client, callback: CallbackQuery):
    if await is_subscribed(client, callback.from_user.id):
        await callback.answer("✅ Verified!", show_alert=True)
        try: await callback.message.delete()
        except: pass
        q = callback.data.replace("verify_sub_", "")
        if q: 
            await callback.message.reply_text(f"✅ Verified! Searching for `{q}`...")
            await send_search_page(callback.message, q, page=0, user_id=callback.from_user.id)
        else:
            await callback.message.reply_text("✅ Verified! You can now use the bot. Type /start.")
    else:
        await callback.answer("❌ You must join BOTH the Channel and the Group!", show_alert=True)

@Client.on_callback_query(filters.regex(r'^spg_'))
@handle_errors
async def search_page_handler(client, callback: CallbackQuery):
    _, page_str, query = callback.data.split("_", 2)
    page = int(page_str)
    await send_search_page(callback, query, page, callback.from_user.id)
    await callback.answer()

@Client.on_callback_query(filters.regex(r'^dl_'))
@handle_errors
async def dl_handler(client, callback: CallbackQuery):
    db_id = callback.data.split("_")[1]
    file = await db.files.find_one({"_id": ObjectId(db_id)})
    if not file: return await callback.answer("❌ File not found.")

    await callback.answer("Sending file... 🚀")
    await db.update_user_stats(callback.from_user.id, points=2, download=True)

    cap = f"🎬 **{file['movie_name']}**\n➠ Quality: {file['quality']}\n\n⚠️ Auto-delete in 20 min."
    msg = await client.copy_message(callback.message.chat.id, CHANNEL_ID, file["message_id"], caption=cap)
    asyncio.create_task(delete_msg(msg, 1200))

@Client.on_callback_query(filters.regex(r'^del_'))
@handle_errors
async def del_file_handler(client, callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Admin only action.", show_alert=True)
        
    db_id = callback.data.split("_")[1]
    success = await db.delete_file(db_id)
    if success:
        await callback.answer("✅ File deleted successfully!", show_alert=True)
        try:
            await callback.message.delete()
        except:
            pass
    else:
        await callback.answer("❌ File not found or already deleted.", show_alert=True)
