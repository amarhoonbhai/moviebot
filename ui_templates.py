from datetime import datetime

def format_movie_card(name, year, rating, language):
    return (
        f"🎬 <b>{name}</b>\n\n"
        f"<blockquote>\n"
        f"▸ Year       : <code>{year}</code>\n"
        f"▸ Rating     : <code>{rating}/10</code>\n"
        f"▸ Language   : <code>{language}</code>\n"
        f"</blockquote>\n\n"
        f"➠ Select a file below to download"
    )

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif 12 <= hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def format_start(users, files, name):
    greeting = get_greeting()
    return (
        f"✨ <b>{greeting}, {name}!</b>\n\n"
        f"Welcome to the ultimate Premium Movie Engine.\n"
        f"Search, track, and download movies instantly while earning gems to climb the global leaderboard! 🏆\n\n"
        f"<blockquote expandable>\n"
        f"▸ Status      : Online 🟢\n"
        f"▸ Users       : {users}+\n"
        f"▸ Files       : {files}+\n"
        f"</blockquote>\n\n"
        f"➠ Use the menu below to navigate"
    )

def get_rank_level(points):
    if points >= 100: return "Legend"
    if points >= 50: return "Elite"
    if points >= 10: return "Pro"
    return "Beginner"

def format_profile(name, p):
    points = p.get('points', 0)
    searches = p.get('total_searches', 0)
    downloads = p.get('total_downloads', 0)
    rank_str = f"#{p.get('rank', 'N/A')}"
    level = get_rank_level(points)
    
    return (
        f"✨ <b>{name}'s Profile</b>\n\n"
        f"<blockquote>\n"
        f"<b>USER STATUS</b>\n\n"
        f"▸ Rank        : {rank_str}\n"
        f"▸ Level       : {level} User\n"
        f"▸ Activity    : Active\n"
        f"</blockquote>\n"
        f"<blockquote>\n"
        f"<b>ACTIVITY</b>\n\n"
        f"▸ Gems        : {points}\n"
        f"▸ Searches    : {searches}\n"
        f"▸ Downloads   : {downloads}\n"
        f"</blockquote>\n\n"
        f"➠ Keep searching to climb leaderboard"
    )

def format_leaderboard(users):
    text = f"🏆 <b>Top Players</b>\n\n<blockquote expandable>\n"
    for i, u in enumerate(users[:10], 1): # Top 10 max
        name = u.get('first_name', 'User')[:15]
        pts = u.get('points', 0)
        text += f"#{i:<2} {name:<15} — {pts} pts\n"
    
    text += "</blockquote>\n\n➠ Earn points by searching & downloading"
    return text

def format_top_searches(searches):
    text = f"🔥 <b>Trending Movies</b>\n\n<blockquote expandable>\n"
    for i, s in enumerate(searches[:10], 1):
        text += f"#{i:<2} {s['query'].upper():<15} — {s['count']} 🔥\n"
        
    text += "</blockquote>\n\n➠ Tap Search below to find your movie"
    return text

def format_quiz(question, options):
    return (
        f"🧩 <b>Flash Quiz</b>\n\n"
        f"<blockquote>\n"
        f"<b>Q: {question}</b>\n\n"
        f"▸ Select the correct answer below\n"
        f"▸ Reward: +5 Gems\n"
        f"</blockquote>\n\n"
        f"➠ Quick, before someone else grabs it!"
    )

def format_stats(s):
    return (
        f"📊 <b>System Intelligence</b>\n\n"
        f"<blockquote>\n"
        f"▸ Users       : {s.get('users', 0)}+\n"
        f"▸ Files       : {s.get('files', 0)}+\n"
        f"▸ Searches    : {s.get('searches', 0)}+\n"
        f"</blockquote>\n\n"
        f"➠ System operating at peak efficiency"
    )

def format_help():
    return (
        f"📖 <b>Command Guide</b>\n\n"
        f"<blockquote>\n"
        f"▸ /search - Find movies\n"
        f"▸ /me - View profile\n"
        f"▸ /leaderboard - Top users\n"
        f"▸ /top - Trending searches\n"
        f"▸ /stats - System stats\n"
        f"</blockquote>\n\n"
        f"➠ Tap buttons below to explore"
    )

def format_about():
    return (
        f"ℹ️ <b>Bot Information</b>\n\n"
        f"<blockquote>\n"
        f"▸ Build       : v5.0 Elite\n"
        f"▸ Status      : Stable ⚡\n"
        f"▸ Network     : @philobots\n"
        f"</blockquote>\n\n"
        f"➠ Experiencing issues? Join support."
    )

def format_guide():
    return format_help()
