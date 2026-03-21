import random
import asyncio
from datetime import datetime, time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import GROUP_ID
from database import db
from ui_templates import format_quiz
from utils import handle_errors

async def send_quiz(bot_client):
    if time(0, 0) <= datetime.now().time() <= time(6, 0): return
    n1, n2 = random.randint(1, 20), random.randint(1, 20)
    ans = n1 + n2
    opts = random.sample(range(max(1, ans-5), ans+10), 3) + [ans]
    random.shuffle(opts)
    
    await db.create_quiz(f"WHAT IS {n1} + {n2}?", ans, opts)
    text = format_quiz(f"{n1} + {n2}", opts)
    btns = [[InlineKeyboardButton(str(o), callback_data=f"qz_{o}")] for o in opts]
    msg = await bot_client.send_message(GROUP_ID, text, reply_markup=InlineKeyboardMarkup(btns))
    
    await asyncio.sleep(60)
    try:
        await msg.edit_text(text + "\n\n⏳ <b>Only 1 minute left!</b>", reply_markup=InlineKeyboardMarkup(btns))
    except: pass
    await asyncio.sleep(60)
    try: await msg.delete()
    except: pass

@Client.on_callback_query(filters.regex(r'^qz_'))
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
