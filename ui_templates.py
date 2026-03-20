def box_text(title, lines):
    """Creates a modern, responsive card-style UI."""
    # Header
    box = f"🎬 <b>{title.upper()}</b>\n"
    box += f"━━━━━━━━━━━━━━━━━━━━\n"
    
    # Content
    for line in lines:
        if "───" in line or "━━━" in line: # Divider
            box += f"────────────────────\n"
        elif "  " in line:
            # Handle Label Value alignment with code blocks for responsiveness
            parts = line.split("  ", 1)
            label = parts[0].strip()
            value = parts[1].strip()
            box += f"<b>{label}:</b> <code>{value}</code>\n"
        else:
            box += f"{line}\n"
    
    box += f"━━━━━━━━━━━━━━━━━━━━\n"
    return box

def format_movie_card(movie_name, year, rating, language):
    """Creates a modern responsive movie card."""
    title = f"{movie_name} ({year})" if year else movie_name
    lines = [
        f"Rating      {rating}/10",
        f"Language    {language}",
        "───",
        "Available Qualities below"
    ]
    return box_text(title, lines)

def format_leaderboard(users):
    """Formats the leaderboard into a sleek card."""
    lines = []
    for i, user in enumerate(users, 1):
        name = user.get('first_name', 'User')[:15]
        gems = user.get('points', 0)
        lines.append(f"{i}. <b>{name}</b>  {gems} Gems")
    
    if not lines: lines = ["No users recorded yet"]
    return box_text("TOP 10 GEMS", lines)

def format_top_searches(searches):
    """Formats top searches into a sleek card."""
    lines = []
    for i, item in enumerate(searches, 1):
        name = item.get('movie_name', item.get('_id', 'Unknown'))[:15]
        count = item.get('total_searches', 0)
        lines.append(f"{i}. <b>{name}</b>  {count}")
    
    if not lines: lines = ["No trending searches"]
    return box_text("TRENDING MOVIES", lines)

def format_quiz(question, options):
    """Formats the math quiz into a sleek card."""
    lines = [
        "Solve the puzzle to win gems!",
        f"<b>Question:</b> <code>{question} = ?</code>",
        "───",
        "<b>Timeout:</b> <code>30 Seconds</code>"
    ]
    return box_text("GEMS QUIZ", lines)

def format_start(name, users=0, files=0):
    """Formats a modern welcome card."""
    lines = [
        f"Welcome, <b>{name}</b>!",
        "───",
        f"Network     <code>{users}+ Users</code>",
        f"Library     <code>{files}+ Files</code>",
        "───",
        "• High Speed Search",
        "• Premium Quality",
        "• Instant Delivery"
    ]
    return box_text("MOVIE BOT PRO", lines)

def format_stats(users, files, searches, points, top_user):
    """Formats a sleek stats card."""
    lines = [
        f"Total Users  {users}",
        f"Total Files  {files}",
        f"Searches     {searches}",
        f"Total Gems   {points}",
        "───",
        f"Top Member   {top_user}"
    ]
    return box_text("SYSTEM STATISTICS", lines)

def format_guide():
    """Formats a modern guide card."""
    lines = [
        "How to use the bot",
        "───",
        "<b>Search</b>      <code>/search movie</code>",
        "<b>Win Gems</b>    <code>Every 20 mins</code>",
        "<b>Auto-Del</b>    <code>Files (20m)</code>"
    ]
    return box_text("BOT GUIDE", lines)

def format_help():
    """Formats a modern help card."""
    lines = [
        "Need assistance?",
        "───",
        "• Use /search to find movies",
        "• Click buttons for downloads",
        "• Win gems for faster access",
        "───",
        "Contact @philobots for support"
    ]
    return box_text("HELP CENTER", lines)

def format_about():
    """Formats a modern about card."""
    lines = [
        "System Information",
        "───",
        "<b>Version</b>      <code>2.5 Pro</code>",
        "<b>Framework</b>    <code>Pyrogram v2</code>",
        "<b>Core</b>         <code>Async Engine</code>",
        "───",
        "Developed for peak performance"
    ]
    return box_text("ABOUT SYSTEM", lines)
