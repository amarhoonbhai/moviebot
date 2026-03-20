import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime

# --- SETTINGS & COLORS ---
BG_COLOR = "#121418"       # Deep dark background
CARD_COLOR = "#1e2126"     # Slightly lighter for the card container
TEXT_COLOR = "#ffffff"     # White text
SUB_TEXT_COLOR = "#a0a4b0" # Light grayish blue for subtitles
ACCENT_COLOR = "#00d0ff"   # Cyan/Blue accent (like the image)
HIGHLIGHT_COLOR = "#ffd700" # Gold for rank 1
RANK_COLORS = {1: "#ffd700", 2: "#c0c0c0", 3: "#cd7f32"} # Gold, Silver, Bronze

def get_fonts():
    # Try modern fonts available on Windows
    fonts = {}
    try:
        fonts['bold'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 38)
        fonts['regular'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 24)
        fonts['small'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 18)
        fonts['title'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 50)
        fonts['handle'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 22)
    except:
        try:
            fonts['bold'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 38)
            fonts['regular'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 24)
            fonts['small'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 18)
            fonts['title'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 50)
            fonts['handle'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 22)
        except:
            d = ImageFont.load_default()
            fonts = {k: d for k in ['bold', 'regular', 'small', 'title', 'handle']}
    return fonts

def create_base_canvas(width, height):
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Draw an elegant card background
    margin = 30
    draw.rounded_rectangle([margin, margin, width-margin, height-margin], radius=25, fill=CARD_COLOR)
    return img, draw

def _draw_avatar(image, avatar_path, x, y, size=240):
    if avatar_path and os.path.exists(avatar_path):
        try:
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar = avatar.resize((size, size), Image.LANCZOS)
            
            mask = Image.new("L", (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, size, size), fill=255)
            
            output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            image.paste(output, (x, y), output)
            
            # Draw beautiful border around it
            draw = ImageDraw.Draw(image)
            draw.ellipse((x-4, y-4, x+size+4, y+size+4), outline=ACCENT_COLOR, width=4)
            return
        except Exception as e:
            print(f"Avatar error: {e}")
            pass
            
    # Default Avatar 
    draw = ImageDraw.Draw(image)
    draw.ellipse((x, y, x+size, y+size), outline=ACCENT_COLOR, width=4)
    # Centered default text if font is missing
    # We will just leave an empty ring or a simple placeholder


def generate_profile_card(full_name, username, user_id, bio, rank, gems, searches, downloads, joined, avatar_path=None):
    """Generates a beautiful profile card mimicking the reference aesthetic."""
    width, height = 800, 480
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    # Define Layout
    avatar_size = 220
    avatar_x, avatar_y = 60, 90
    _draw_avatar(img, avatar_path, avatar_x, avatar_y, avatar_size)
    
    # Text Layout on the right
    text_x = 340
    
    # Name & Role Header
    title = f"{full_name.upper()} ~ RANK #{rank}"
    draw.text((text_x, 60), title, font=fonts['title'], fill=TEXT_COLOR)
    
    # Username handle and ID
    handle = f"@{username}  |  ID: {user_id}"
    draw.text((text_x, 120), handle, font=fonts['handle'], fill=SUB_TEXT_COLOR)
    
    # Bio
    draw.text((text_x, 160), "Bio:", font=fonts['handle'], fill=ACCENT_COLOR)
    display_bio = bio[:45] + "..." if len(bio) > 45 else bio
    draw.text((text_x+45, 160), display_bio, font=fonts['handle'], fill=TEXT_COLOR)
    
    draw.text((text_x, 210), "User Account", font=fonts['bold'], fill=ACCENT_COLOR)
    
    # Stats row
    def draw_stat(sx, sy, label, value):
        draw.text((sx, sy), label.upper(), font=fonts['small'], fill=SUB_TEXT_COLOR)
        draw.text((sx, sy+25), str(value), font=fonts['bold'], fill=TEXT_COLOR)
    
    draw_stat(text_x, 270, "Gems", gems)
    draw_stat(text_x + 140, 270, "Searches", searches)
    draw_stat(text_x + 280, 270, "Downloads", downloads)
    
    # Joined Date
    draw.text((text_x, 350), f"Member since: {joined}", font=fonts['small'], fill=SUB_TEXT_COLOR)
    
    output_path = f"profile_{user_id}.png"
    img.save(output_path)
    return output_path

def generate_leaderboard_card(users):
    """Generates an aesthetic leaderboard card image."""
    width = 800
    row_height = 80
    header_height = 120
    height = header_height + (len(users) * row_height) + 60
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 50), "🏆 GLOBAL LEADERBOARD", font=fonts['title'], fill=ACCENT_COLOR)
    
    y = header_height + 20
    for i, u in enumerate(users, 1):
        color = RANK_COLORS.get(i, TEXT_COLOR)
        name = u.get('first_name', 'Unknown User')
        points = u.get('points', 0)
        
        # Rank
        draw.text((60, y), f"#{i}", font=fonts['bold'], fill=color)
        # Name
        draw.text((150, y), name, font=fonts['bold'], fill=TEXT_COLOR)
        # Score
        score_text = f"{points} GEMS"
        # right align score roughly
        draw.text((600, y), score_text, font=fonts['bold'], fill=ACCENT_COLOR)
        
        y += row_height
        
    output_path = "leaderboard_card.png"
    img.save(output_path)
    return output_path

def generate_top_searches_card(searches):
    """Generates an aesthetic trending searches card."""
    width = 800
    row_height = 70
    header_height = 120
    height = header_height + (len(searches) * row_height) + 60
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 50), "🔥 TRENDING SEARCHES", font=fonts['title'], fill=ACCENT_COLOR)
    
    y = header_height + 20
    for i, s in enumerate(searches, 1):
        query = s['query'].upper()
        count = s['count']
        
        # Rank
        draw.text((60, y), f"{i}.", font=fonts['bold'], fill=SUB_TEXT_COLOR)
        # Movie query
        draw.text((120, y), query, font=fonts['bold'], fill=TEXT_COLOR)
        # Views/Count
        draw.text((650, y), f"{count} 🔥", font=fonts['bold'], fill=HIGHLIGHT_COLOR)
        
        y += row_height
        
    output_path = "top_searches_card.png"
    img.save(output_path)
    return output_path

def generate_stats_card(stats):
    """Generates an aesthetic system statistics card."""
    width, height = 800, 400
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 50), "📊 SYSTEM STATISTICS", font=fonts['title'], fill=ACCENT_COLOR)
    
    # Draw nice big numbers
    def draw_big_stat(x, y, label, value):
        draw.text((x, y), str(value), font=fonts['title'], fill=TEXT_COLOR)
        draw.text((x, y+60), label.upper(), font=fonts['handle'], fill=SUB_TEXT_COLOR)
        
    draw_big_stat(80, 180, "Verified Users", f"{stats.get('users', 0):,}+")
    draw_big_stat(350, 180, "Indexed Files", f"{stats.get('files', 0):,}+")
    draw_big_stat(600, 180, "Total Searches", f"{stats.get('searches', 0):,}+")
    
    draw.text((60, 320), "Status: Online 🟢    |    Latency: <50ms", font=fonts['small'], fill=ACCENT_COLOR)
    
    output_path = "stats_card.png"
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test renders
    generate_profile_card("Kurup Lastname", "kurup_pro", 1234567, "I am the developer.", 1, 9999, 450, 120, "20 Mar 2026")
    generate_leaderboard_card([{"first_name": "Kurup", "points": 9999}, {"first_name": "Alice", "points": 8000}])
    generate_top_searches_card([{"query": "Inception", "count": 1500}, {"query": "Interstellar", "count": 1200}])
    generate_stats_card({"users": 15000, "files": 450000, "searches": 900000})
