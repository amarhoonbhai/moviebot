def box_text(title, lines):
    """Formats text into a box-style structure."""
    box = f"┌────────────────────────────\n"
    box += f"│ {title}\n"
    box += f"├────────────────────────────\n"
    for line in lines:
        box += f"│ {line}\n"
    box += f"└────────────────────────────\n"
    return box

def format_movie_card(movie_name, year, rating, language):
    """Creates a premium movie card."""
    title = f"{movie_name.upper()} ({year})" if year else movie_name.upper()
    lines = [
        f"Rating     {rating}/10",
        f"Language   {language}",
        "├────────────────────────────",
        "│ Formats"
    ]
    card = box_text(title, lines)
    card += "\n➠ Select quality"
    return card

def format_leaderboard(users):
    """Formats the leaderboard into a box-style structure."""
    lines = []
    for i, user in enumerate(users, 1):
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
        lines.append(f"{i}. {name:<15} {user.get('points', 0)} pts")
    
    return box_text("TOP USERS", lines)

def format_top_searches(searches):
    """Formats top searches into a box-style structure."""
    lines = []
    for i, item in enumerate(searches, 1):
        lines.append(f"{i}. {item.get('movie_name', 'Unknown'):<15} {item.get('total_searches', 0)}")
    
    if not lines:
        lines = ["No searches yet"]
    return box_text("TOP SEARCHES", lines)

def format_top_searches_fixed(searches):
    """Formats top searches into a box-style structure."""
    lines = []
    for i, item in enumerate(searches, 1):
        name = item.get('movie_name', item.get('_id', 'Unknown'))
        lines.append(f"{i}. {name:<15} {item.get('total_searches', 0)}")
    
    if not lines:
        lines = ["No searches yet"]
    
    return box_text("TOP SEARCHES", lines)

def format_quiz(question, options):
    """Formats the math quiz."""
    box = box_text("MATH QUIZ", [f"{question} = ?"])
    box += "\n➠ Choose answer"
    return box

def format_start(name, users=0, files=0):
    """Formats an enhanced start command message."""
    lines = [
        f"Welcome, {name}!",
        "├────────────────────────────",
        f"Files      {files}+",
        f"Users      {users}+",
        "├────────────────────────────",
        "Interactive search system",
        "High speed downloads",
        "Math quiz rewards"
    ]
    box = box_text("MOVIE BOT", lines)
    box += "\n➠ Fast and Reliable"
    box += "\n➠ Earn points by playing quiz"
    return box

def format_stats(users, files, searches, points, top_user):
    """Formats an enhanced stats message."""
    lines = [
        f"Total Users    {users}",
        f"Total Files    {files}",
        "├───────────────────────────",
        f"Total Searches  {searches}",
        f"Total Points    {points}",
        "├───────────────────────────",
        f"Top User : {top_user}"
    ]
    return box_text("BOT STATISTICS", lines)

def format_guide():
    """Formats the guide command message."""
    lines = [
        "Search: /search <movie name>",
        "Points: Search(+1), DL(+2), Quiz(+5)",
        "Quiz: Every 30 mins (Quick win!)",
        "Limits: Files delete after 20 mins"
    ]
    return box_text("BOT GUIDE", lines)
