import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from datetime import datetime

# --- SETTINGS & COLORS ---
BG_COLOR = "#0b0c10"       # Elite super dark background
CARD_COLOR = "#14151a"     # Slightly lighter for the card container
TEXT_COLOR = "#ffffff"     # White text
SUB_TEXT_COLOR = "#808492" # Slate gray for subtitles
ACCENT_COLOR = "#00f0ff"   # Neon Cyan/Blue accent
HIGHLIGHT_COLOR = "#ffd700" # Gold
RANK_COLORS = {1: "#ffd700", 2: "#c0c0c0", 3: "#cd7f32"} # Gold, Silver, Bronze

def get_fonts():
    fonts = {}
    try: # Try modern fonts available on Windows
        fonts['bold'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 36)
        fonts['largest'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 60)
        fonts['regular'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 26)
        fonts['small'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 20)
        fonts['title'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 46)
        fonts['handle'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 28)
        fonts['stats_num'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 55)
        fonts['badge'] = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 24)
    except:
        try:
            fonts['bold'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 36)
            fonts['largest'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 60)
            fonts['regular'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 26)
            fonts['small'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 20)
            fonts['title'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 46)
            fonts['handle'] = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 28)
            fonts['stats_num'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 55)
            fonts['badge'] = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 24)
        except:
            d = ImageFont.load_default()
            fonts = {k: d for k in ['bold', 'largest', 'regular', 'small', 'title', 'handle', 'stats_num', 'badge']}
    return fonts

def create_base_canvas(width, height):
    img = Image.new("RGBA", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    margin = 25
    draw.rounded_rectangle([margin, margin, width-margin, height-margin], radius=35, fill=CARD_COLOR)
    return img, draw

def _draw_avatar(image, avatar_path, x, y, size=240):
    # Glow effect layer
    glow_size = size + 60
    glow = Image.new("RGBA", (glow_size, glow_size), (0,0,0,0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse((20, 20, glow_size-20, glow_size-20), fill=(0, 240, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    image.paste(glow, (x - 30, y - 30), glow)
    
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
        except Exception as e:
            pass
            
    # Draw border
    draw = ImageDraw.Draw(image)
    draw.ellipse((x-4, y-4, x+size+4, y+size+4), outline=ACCENT_COLOR, width=5)

def get_badge_title(gems, rank):
    if str(rank) == "1": return "TOP 1", HIGHLIGHT_COLOR
    if gems >= 100: return "LEGEND", "#ff00ff"
    if gems >= 50: return "ELITE", "#00ff88"
    if gems >= 10: return "PRO", ACCENT_COLOR
    return "BEGINNER", SUB_TEXT_COLOR

def generate_profile_card(full_name, username, user_id, bio, rank, gems, searches, downloads, joined, avatar_path=None):
    width, height = 900, 520
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    # Avatar
    avatar_size = 250
    avatar_x, avatar_y = 60, 100
    _draw_avatar(img, avatar_path, avatar_x, avatar_y, avatar_size)
    
    text_x = 360
    
    # Title & Badge
    badge_text, badge_color = get_badge_title(gems, rank)
    
    # Draw Badge Box
    draw.rounded_rectangle([text_x, 70, text_x + 140, 105], radius=8, fill=badge_color)
    # Centering badge text manually approx
    draw.text((text_x + 15, 74), badge_text, font=fonts['badge'], fill="#000000")
    
    # Name
    safe_name = full_name.upper()[:15]
    draw.text((text_x, 120), safe_name, font=fonts['largest'], fill=TEXT_COLOR)
    
    # Username handle and ID
    handle = f"@{username}   •   ID: {user_id}"
    draw.text((text_x, 195), handle, font=fonts['handle'], fill=SUB_TEXT_COLOR)
    
    # Divider line
    draw.line([(text_x, 245), (width - 60, 245)], fill="#2a2d36", width=2)
    
    # Stats row (Centered numbers above labels)
    def draw_stat(cx, cy, label, value):
        # Value (large)
        v_str = str(value)
        # Approximate centering
        vw = len(v_str) * 20 # rough width
        draw.text((cx - vw//2, cy), v_str, font=fonts['stats_num'], fill=TEXT_COLOR)
        # Label (small)
        lw = len(label) * 8
        draw.text((cx - lw//2 + 5, cy + 65), label.upper(), font=fonts['small'], fill=SUB_TEXT_COLOR)
    
    draw_stat(text_x + 50, 270, "GEMS", gems)
    draw_stat(text_x + 220, 270, "SEARCHES", searches)
    draw_stat(text_x + 390, 270, "DOWNLOADS", downloads)
    
    # Bottom Section
    draw.line([(text_x, 385), (width - 60, 385)], fill="#2a2d36", width=2)
    
    lvl = (gems // 10) + 1
    xp = gems % 10
    draw.text((text_x, 410), f"LEVEL {lvl}  |  {xp}/10 XP", font=fonts['bold'], fill=ACCENT_COLOR)
    draw.text((width - 250, 420), f"Member since: {joined}", font=fonts['small'], fill=SUB_TEXT_COLOR)
    
    output_path = f"profile_{user_id}.png"
    img.save(output_path)
    return output_path

def generate_leaderboard_card(users):
    width = 900
    row_height = 85
    header_height = 130
    height = header_height + (len(users) * row_height) + 60
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 50), "🏆 ELITE LEADERBOARD", font=fonts['largest'], fill=ACCENT_COLOR)
    
    y = header_height + 20
    for i, u in enumerate(users, 1):
        color = RANK_COLORS.get(i, TEXT_COLOR)
        name = u.get('first_name', 'Unknown')
        points = u.get('points', 0)
        
        draw.text((70, y), f"#{i}", font=fonts['title'], fill=color)
        draw.text((180, y), name[:15], font=fonts['title'], fill=TEXT_COLOR)
        
        score_text = f"{points} GEMS"
        draw.text((700, y), score_text, font=fonts['title'], fill=ACCENT_COLOR)
        
        y += row_height
        
    output_path = "leaderboard_card.png"
    img.save(output_path)
    return output_path

def generate_top_searches_card(searches):
    width = 900
    row_height = 80
    header_height = 130
    height = header_height + (len(searches) * row_height) + 60
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 50), "🔥 TRENDING NOW", font=fonts['largest'], fill=ACCENT_COLOR)
    
    y = header_height + 20
    for i, s in enumerate(searches, 1):
        query = s['query'].upper()[:20]
        count = s['count']
        
        draw.text((70, y), f"{i}.", font=fonts['title'], fill=SUB_TEXT_COLOR)
        draw.text((160, y), query, font=fonts['title'], fill=TEXT_COLOR)
        draw.text((730, y), f"{count} 🔥", font=fonts['title'], fill=HIGHLIGHT_COLOR)
        
        y += row_height
        
    output_path = "top_searches_card.png"
    img.save(output_path)
    return output_path

def generate_stats_card(stats):
    width, height = 900, 450
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((60, 60), "📊 SYSTEM INTELLIGENCE", font=fonts['largest'], fill=ACCENT_COLOR)
    
    def draw_big_stat(x, y, label, value):
        draw.text((x, y), str(value), font=fonts['largest'], fill=TEXT_COLOR)
        draw.text((x, y+75), label.upper(), font=fonts['handle'], fill=SUB_TEXT_COLOR)
        
    draw_big_stat(80, 200, "Verified Users", f"{stats.get('users', 0):,}+")
    draw_big_stat(380, 200, "Indexed Files", f"{stats.get('files', 0):,}+")
    draw_big_stat(650, 200, "Total Searches", f"{stats.get('searches', 0):,}+")
    
    draw.line([(60, 360), (width - 60, 360)], fill="#2a2d36", width=2)
    draw.text((60, 380), "Status: 🟢 ONLINE   |   Latency: <30ms", font=fonts['handle'], fill=ACCENT_COLOR)
    
    output_path = "stats_card.png"
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    generate_profile_card("KURUP", "kurup_pro", 1234567, "Bio", 1, 154, 45, 12, "20 Mar 2026")
    generate_leaderboard_card([{"first_name": "Kurup", "points": 154}, {"first_name": "Alice", "points": 80}])
    generate_top_searches_card([{"query": "Inception", "count": 1500}, {"query": "Interstellar", "count": 1200}])
    generate_stats_card({"users": 15000, "files": 450000, "searches": 900000})
