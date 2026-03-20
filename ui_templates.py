from datetime import datetime

def format_movie_card(name, year, rating, language):
    """Premium Professional Movie Card."""
    return (
        f"🎬 <b>{name}</b>\n"
        f"────────────────────\n"
        f"⮩ 🗓️ <b>Year</b>: <code>{year}</code>\n"
        f"⮩ ⭐ <b>Rating</b>: <code>{rating}/10</code>\n"
        f"⮩ 🌐 <b>Language</b>: <code>{language}</code>\n"
        f"────────────────────\n"
        f"➲ <i>Powered by Premium Movie Engine</i>"
    )

def format_start(users, files, name):
    """Dynamic Professional Start Message."""
    return (
        f"👋 <b>Welcome back, {name}!</b>\n\n"
        f"Experience the most advanced <b>Movie Search Engine</b> on Telegram. 🎬\n\n"
        f"➲ <b>SYSTEM STATUS</b>\n"
        f"🔹 <b>Verified Users</b>: <code>{users}+</code>\n"
        f"🔸 <b>Indexed Files</b>: <code>{files}+</code>\n\n"
        f"➤ <i>Use /help to explore all features.</i>"
    )

def format_profile(p):
    """Detailed Professional User Profile."""
    joined = p.get('joined_at', datetime.now()).strftime("%d %b %Y")
    points = p.get('points', 0)
    
    # Progress Bar
    level_progress = (points % 100) // 10
    bar = "▰" * level_progress + "▱" * (10 - level_progress)

    return (
        f"👤 <b>USER DASHBOARD</b>\n"
        f"────────────────────\n"
        f"🏆 <b>Global Rank</b>: <code>#{p.get('rank', 'N/A')}</code>\n"
        f"💎 <b>Total Gems</b>: <code>{points}</code>\n\n"
        f"➲ <b>LOYALTY PROGRESS</b>\n"
        f"⮩ <code>{bar}</code>\n\n"
        f"➲ <b>ACTIVITY STATS</b>\n"
        f"🔹 Searches: <code>{p.get('total_searches', 0)}</code>\n"
        f"🔸 Downloads: <code>{p.get('total_downloads', 0)}</code>\n\n"
        f"📅 <b>Membership</b>: <code>{joined}</code>\n"
        f"────────────────────"
    )

def format_leaderboard(users):
    """Premium Leaderboard."""
    text = "🏆 <b>TOP PERFORMERS</b>\n────────────────────\n"
    for i, u in enumerate(users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        name = u.get('first_name') or "User"
        text += f"{medal} #{i} | {name} | {u.get('points', 0)} 💎\n"
    text += "────────────────────"
    return text

def format_top_searches(searches):
    """Professional Trending Searches."""
    text = "🔥 <b>TRENDING MOVIES</b>\n────────────────────\n"
    for i, s in enumerate(searches, 1):
        text += f"➲ {i}. {s['query'].upper()} ({s['count']} 🔥)\n"
    text += "────────────────────"
    return text

def format_quiz(question, options):
    return (
        f"🧩 <b>FLASH QUIZ!</b>\n"
        f"────────────────────\n"
        f"<b>Q: {question}</b>\n\n"
        f"➲ <b>Select Answer:</b>\n"
        f"   {', '.join(map(str, options))}\n"
        f"────────────────────\n"
        f"💰 Reward: <b>+5 Gems</b>"
    )

def format_help():
    return (
        f"📖 <b>ADVANCED COMMAND GUIDE</b>\n"
        f"────────────────────\n"
        f"➲ <b>PUBLIC COMMANDS</b>\n"
        f"➤ `/search` - Find any movie\n"
        f"➤ `/me` - User stats & level\n"
        f"➤ `/leaderboard` - Top users\n"
        f"➤ `/top` - Trending searches\n"
        f"➤ `/stats` - System statistics\n\n"
        f"➲ <b>ADMIN CONTROL</b>\n"
        f"➤ `/requests` - Pending requests\n"
        f"➤ `/broadcast` - Mass message\n"
        f"────────────────────\n"
        f"⚠️ <i>Join Force Channel for Access</i>"
    )

def format_about():
    return (
        f"ℹ️ <b>BOT INFORMATION</b>\n"
        f"────────────────────\n"
        f"🔹 Build: <code>v4.5 Enterprise</code>\n"
        f"🔹 Status: <code>Stable ⚡</code>\n"
        f"🔹 Database: <code>Cluster High Speed ☁️</code>\n"
        f"────────────────────\n"
        f"Developed by @philobots Network."
    )

def format_guide():
    return format_help()
