from datetime import datetime

def format_movie_card(name, year, rating, language):
    """Premium Box-Style Movie Card."""
    return (
        f"🎬 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🗓️ <b>Year</b>: {year}\n"
        f"⭐ <b>Rating</b>: {rating}/10\n"
        f"🌐 <b>Language</b>: {language}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <i>Fastest Telegram Movie Bot</i>"
    )

def format_start(users, files, name):
    """Dynamic Professional Start Message."""
    return (
        f"👋 <b>Hello, {name}!</b>\n\n"
        f"Welcome to the <b>Premium Movie Bot</b> 🎬\n\n"
        f"🚀 <b>System Live</b>\n"
        f"👥 Users: {users}+\n"
        f"📂 Files: {files}+\n\n"
        f"Search any movie using: `/search movie_name` 🎯"
    )

def format_profile(p):
    """Detailed Professional User Profile."""
    joined = p.get('joined_at', datetime.now()).strftime("%d %b %Y")
    return (
        f"👤 <b>USER PROFILE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏅 <b>Global Rank</b>: #{p.get('rank', 'N/A')}\n"
        f"💎 <b>Gems</b>: {p.get('points', 0)}\n\n"
        f"📊 <b>Stats</b>\n"
        f"🔍 Searches: {p.get('total_searches', 0)}\n"
        f"📥 Downloads: {p.get('total_downloads', 0)}\n"
        f"📅 Joined: {joined}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

def format_leaderboard(users):
    """Premium Leaderboard."""
    text = "🏆 <b>TOP PERFORMERS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, u in enumerate(users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "✨"
        name = u.get('first_name') or "User"
        text += f"{medal} #{i} | {name} | {u.get('points', 0)} 💎\n"
    text += "━━━━━━━━━━━━━━━━━━━━"
    return text

def format_top_searches(searches):
    """Professional Trending Searches."""
    text = "🔥 <b>TRENDING MOVIES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, s in enumerate(searches, 1):
        text += f"{i}. {s['query'].upper()} ({s['count']} 🔥)\n"
    text += "━━━━━━━━━━━━━━━━━━━━"
    return text

def format_quiz(question, options):
    return (
        f"🧩 <b>FLASH QUIZ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Q: {question}</b>\n\n"
        f"Options: {', '.join(map(str, options))}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Reward: <b>+5 Gems</b>"
    )

def format_help():
    return (
        f"📖 <b>BOT GUIDE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 `/search` - Find any movie\n"
        f"👤 `/me` - Check your profile\n"
        f"🏆 `/leaderboard` - Top users\n"
        f"🔥 `/top` - Trending movies\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <i>Join Force Channel for Access</i>"
    )

def format_about():
    return (
        f"ℹ️ <b>ABOUT BOT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Build: <b>v4.0 Professional</b>\n"
        f"Status: <b>Active ⚡</b>\n"
        f"Database: <b>MongoDB Cloud ☁️</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Developed with ❤️ for the community."
    )

def format_guide():
    return format_help()
