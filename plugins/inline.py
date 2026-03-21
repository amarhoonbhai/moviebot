from pyrogram import Client, enums
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from tmdb_helper import get_movie_details
from ui_templates import format_movie_card
import logging

logger = logging.getLogger(__name__)

@Client.on_inline_query()
async def inline_search(client, query: InlineQuery):
    text = query.query.strip()
    if len(text) < 2:
        return await query.answer(
            results=[],
            switch_pm_text="Type a movie name to search...",
            switch_pm_parameter="start"
        )
    
    results = await db.search_movies(text, limit=15)
    if not results:
        return await query.answer(
            results=[],
            switch_pm_text="😔 No results found. Click to request.",
            switch_pm_parameter="start"
        )
        
    inline_results = []
    movies_found = {}
    for r in results:
        m_name = r.get("movie_name")
        if m_name not in movies_found:
            movies_found[m_name] = r
            
    for m_name, data in movies_found.items():
        year = data.get("year", "0000")
        metadata = await get_movie_details(m_name, year)
        
        name = metadata['title'].upper() if metadata else m_name.upper()
        
        lang = data.get('language', 'Multi')
        if lang == "Unknown": lang = "Multi"
        
        runtime = metadata.get('runtime', 'N/A') if metadata else 'N/A'
        genres = metadata.get('genres', 'N/A') if metadata else 'N/A'
        director = metadata.get('director', 'Unknown') if metadata else 'Unknown'
        cast = metadata.get('cast', 'Unknown') if metadata else 'Unknown'
        plot = metadata.get('plot', 'No plot available') if metadata else 'No plot available.'
        rating = metadata['rating'] if metadata else "N/A"
        
        card_text = format_movie_card(name, year, rating, lang, runtime, genres, director, cast, plot)
        
        # Deep link to start bot with file ID
        bot_username = client.me.username if client.me else "Bot"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download Movie", url=f"https://t.me/{bot_username}?start=dl_{data['_id']}")]])
        
        thumb = metadata.get('poster') if metadata else None
        
        inline_results.append(
            InlineQueryResultArticle(
                title=name,
                description=f"Year: {year} | Rating: {rating}/10",
                thumb_url=thumb,
                input_message_content=InputTextMessageContent(
                    message_text=card_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False if thumb else True
                ),
                reply_markup=btn
            )
        )
        
    await query.answer(results=inline_results, cache_time=5)
