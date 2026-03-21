from datetime import datetime

# --- DESIGN SYSTEM ---
DOT = "▪"

def format_movie_card(name, year, rating, language, runtime, genres, director, cast, plot, seasons=None):
    season_str = f" | <b>S:</b> <code>{seasons}</code>" if seasons else ""
    return (
        f"🎬 <b>{str(name).upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{DOT} Release Year:</b>  <code>{year}</code> | <b>⏱</b> <code>{runtime}</code>{season_str}\n"
        f"<b>{DOT} Genres:</b>  <code>{genres}</code>\n"
        f"<b>{DOT} TMDb Rating:</b>  <code>{rating}/10</code>\n"
        f"<b>{DOT} Director:</b>  <code>{director}</code>\n"
        f"<b>{DOT} Cast:</b>  <code>{cast}</code>\n"
        f"<b>{DOT} Audio Track:</b>  <code>{language}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 <i>{plot}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Select your preferred quality below</i>"
    )

def get_greeting():
    hour = datetime.now().hour
    if hour < 12: return "Good morning"
    elif 12 <= hour < 18: return "Good afternoon"
    else: return "Good evening"

def format_start(users, files, name):
    return (
        f"<b>{get_greeting()}, {name}</b>\n\n"
        f"Welcome to the Movie Database. Search, track, and download movies instantly.\n\n"
        f"<b>System Status</b>\n"
        f"<b>{DOT} Active Users:</b> <code>{users:,}</code>\n"
        f"<b>{DOT} Indexed Files:</b> <code>{files:,}</code>\n\n"
        f"<i>Use the menu to navigate</i>"
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
        f"<b>User Profile:</b> {name}\n\n"
        f"<b>Status</b>\n"
        f"<b>{DOT} Global Rank:</b> <code>{rank_str}</code>\n"
        f"<b>{DOT} Authority Level:</b> <code>{level}</code>\n\n"
        f"<b>Activity</b>\n"
        f"<b>{DOT} Total Gems:</b> <code>{points}</code>\n"
        f"<b>{DOT} Searches:</b> <code>{searches}</code>\n"
        f"<b>{DOT} Downloads:</b> <code>{downloads}</code>\n"
    )

def format_leaderboard(users):
    text = f"<b>Global Leaderboard</b>\n\n"
    for i, u in enumerate(users[:10], 1): # Top 10 max
        name = u.get('first_name', 'User')[:15]
        pts = u.get('points', 0)
        prefix = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"<b>{i}.</b>"
        text += f"{prefix} {name} <b>—</b> <code>{pts} pts</code>\n"
    
    text += "\n<i>Earn more points by participating</i>"
    return text

def format_daily(points_added, new_total):
    return (
        f"<b>Daily Reward Claimed!</b>\n\n"
        f"<b>{DOT} Received:</b> <code>+{points_added} Gems</code>\n"
        f"<b>{DOT} Total Balance:</b> <code>{new_total}</code>\n\n"
        f"<i>Come back in 24 hours for more</i>"
    )

def format_top_searches(searches):
    text = f"<b>Trending Searches</b>\n\n"
    for i, s in enumerate(searches[:10], 1):
        try:
            query_name = s['query'].title()
        except KeyError:
            query_name = "Unknown"
        text += f"<b>{i}.</b> {query_name} <b>—</b> <code>{s.get('count', 0)} times</code>\n"
        
    return text

def format_quiz(question, options):
    return (
        f"<b>Flash Quiz</b>\n\n"
        f"<b>Question:</b> {question}\n\n"
        f"<b>{DOT} Reward:</b> <code>+5 Gems</code>\n"
        f"<b>{DOT} Rule:</b> First correct answer wins.\n\n"
        f"<i>Select your answer below</i>"
    )

def format_stats(s):
    return (
        f"<b>System Intelligence</b>\n\n"
        f"<b>{DOT} Total Users:</b> <code>{s.get('users', 0):,}</code>\n"
        f"<b>{DOT} Movies Indexed:</b> <code>{s.get('files', 0):,}</code>\n"
        f"<b>{DOT} Lifetime Searches:</b> <code>{s.get('searches', 0):,}</code>\n"
    )

def format_help():
    return (
        f"<b>Command Guide</b>\n\n"
        f"<b>{DOT}</b> <code>/search</code> - Find movies in the database\n"
        f"<b>{DOT}</b> <code>/me</code> - View your profile\n"
        f"<b>{DOT}</b> <code>/leaderboard</code> - View top users\n"
        f"<b>{DOT}</b> <code>/top</code> - Discover trending movies\n"
        f"<b>{DOT}</b> <code>/stats</code> - View live system stats\n"
    )

def format_about():
    return (
        f"<b>System Information</b>\n\n"
        f"<b>{DOT} Core Build:</b> <code>v7.0 Minimalist</code>\n"
        f"<b>{DOT} Server Status:</b> <code>Online</code>\n"
        f"<b>{DOT} Network:</b> <code>@philobots</code>\n"
    )

def format_guide():
    return format_help()
