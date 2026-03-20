def box_text(title, lines):
    """Creates a professional fixed-width box UI (30 chars)."""
    width = 30
    # Header
    box = f"┌{'─' * width}\n"
    box += f"│ <b>{title.upper()}</b>\n"
    box += f"├{'─' * width}\n"
    
    # Content
    for line in lines:
        if "───" in line: # Decorative divider
            box += f"├{'─' * width}\n"
        else:
            # Handle Label Value alignment (fixed 12 char label width)
            if "  " in line:
                parts = line.split("  ", 1)
                label = parts[0].strip()
                value = parts[1].strip()
                padding = max(0, 12 - len(label))
                box += f"│ {label}{' ' * padding} {value}\n"
            else:
                box += f"│ {line}\n"
    
    box += f"└{'─' * width}\n"
    return box

def format_movie_card(movie_name, year, rating, language):
    """Creates a premium movie card matching the new style."""
    title = f"{movie_name} ({year})" if year else movie_name
    lines = [
        f"Rating      {rating}/10",
        f"Language    {language}",
        "───",
        "Formats"
    ]
    card = box_text(title, lines)
    card += "\n➠ Select quality"
    return card

def format_leaderboard(users):
    """Formats the leaderboard into a clean box UI with Gems."""
    lines = []
    for i, user in enumerate(users, 1):
        name = user.get('first_name', 'User')[:12]
        gems = user.get('points', 0)
        lines.append(f"{i}. {name}  {gems} Gems")
    
    if not lines: lines = ["No users yet"]
    return box_text("TOP 10 GEMS", lines)

def format_top_searches(searches):
    """Formats top searches into a clean box UI."""
    lines = []
    for i, item in enumerate(searches, 1):
        name = item.get('movie_name', item.get('_id', 'Unknown'))[:15]
        count = item.get('total_searches', 0)
        lines.append(f"{i}. {name}  {count}")
    
    if not lines: lines = ["No searches yet"]
    return box_text("TRENDING NOW", lines)

def format_quiz(question, options):
    """Formats the math quiz into a clean box UI."""
    lines = [
        "Solve this puzzle",
        f"<b>{question} = ?</b>",
        "───",
        "Timeout     30 sec"
    ]
    box = box_text("GEMS QUIZ", lines)
    box += "\n➠ Select one option"
    return box

def format_start(name, users=0, files=0):
    """Formats the enhanced start welcome panel."""
    lines = [
        f"Welcome, {name}!",
        "───",
        f"Files       {files}+",
        f"Users       {users}+",
        "───",
        "Fast movie search",
        "High quality files",
        "Instant delivery"
    ]
    box = box_text("MOVIE BOT", lines)
    box += "\n➠ Use /search movie name"
    return box

def format_stats(users, files, searches, points, top_user):
    """Formats the enhanced stats message."""
    lines = [
        f"Users       {users}",
        f"Files       {files}",
        f"Searches    {searches}",
        f"Total Gems  {points}",
        "───",
        f"Top User    {top_user}"
    ]
    return box_text("BOT STATISTICS", lines)

def format_guide():
    """Formats the guide command message."""
    lines = [
        "Search      /search movie",
        "Gems        Win in quizzes",
        "Quiz        Every 20 mins",
        "Limits      20 min auto-del"
    ]
    return box_text("BOT GUIDE", lines)

def format_help():
    """Formats the help command message."""
    lines = [
        "Search      Movie keywords",
        "Download    Select quality",
        "Leaderboard Track gems",
        "Support     Contact admin",
        "───",
        "Use buttons below for links"
    ]
    return box_text("HELP CENTER", lines)

def format_about():
    """Formats the about command message."""
    lines = [
        "Version     2.0 Pro",
        "Developer   @Antigravity",
        "Framework   Pyrogram",
        "Database    MongoDB",
        "───",
        "The most advanced movie bot"
    ]
    return box_text("ABOUT BOT", lines)
