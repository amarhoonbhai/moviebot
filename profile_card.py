import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

# --- SETTINGS & COLORS ---
BG_COLOR = "#0c0d12"       # Deep app background
CARD_COLOR = "#181a24"     # Sleek card container
TEXT_COLOR = "#ffffff"     # White text
SUB_TEXT_COLOR = "#8b94a0" # Cool slate gray
ACCENT_COLOR = "#00e5ff"   # Electric Cyan
HIGHLIGHT_COLOR = "#ffcc00" # Premium Gold
RANK_COLORS = {1: "#ffcc00", 2: "#e0e0e0", 3: "#cd7f32"} # Gold, Silver, Bronze

def get_fonts():
    fonts = {}
    try:
        # High quality built-in Windows fonts
        b_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
        r_path = "C:\\Windows\\Fonts\\segoeui.ttf"
        bl_path = b_path 
        # Attempt load to verify existence
        ImageFont.truetype(b_path, 10) 
    except:
        try:
            b_path = "C:\\Windows\\Fonts\\arialbd.ttf"
            r_path = "C:\\Windows\\Fonts\\arial.ttf"
            bl_path = b_path
            ImageFont.truetype(b_path, 10)
        except:
            d = ImageFont.load_default()
            return {k: d for k in ['name', 'title', 'handle', 'stats_num', 'badge', 'small']}
        
    # Super massive typography for mobile readability
    fonts['name'] = ImageFont.truetype(bl_path, 44)     # Enormous Name
    fonts['title'] = ImageFont.truetype(b_path, 34)     # Section Titles
    fonts['handle'] = ImageFont.truetype(r_path, 20)    # @username
    fonts['stats_num'] = ImageFont.truetype(bl_path, 40) # Huge Numbers
    fonts['badge'] = ImageFont.truetype(b_path, 18)     # Badges
    fonts['small'] = ImageFont.truetype(b_path, 14)     # Small caps tags
    return fonts

def create_base_canvas(width, height):
    img = Image.new("RGBA", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    margin = 15
    draw.rounded_rectangle([margin, margin, width-margin, height-margin], radius=25, fill=CARD_COLOR)
    return img, draw

def _draw_avatar(image, avatar_path, x, y, size=180):
    # Centered behind avatar glow
    glow_size = size + 60
    glow = Image.new("RGBA", (glow_size, glow_size), (0,0,0,0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse((20, 20, glow_size-20, glow_size-20), fill=(0, 229, 255, 60))
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
        except Exception:
            pass
            
    # Draw thicker neon border
    draw = ImageDraw.Draw(image)
    draw.ellipse((x-4, y-4, x+size+4, y+size+4), outline=ACCENT_COLOR, width=5)

def get_badge_title(gems, rank):
    if str(rank) == "1": return "TOP 1", HIGHLIGHT_COLOR, "#000000"
    if gems >= 100: return "LEGEND", "#9d00ff", "#ffffff"
    if gems >= 50: return "ELITE", "#00ff88", "#000000"
    if gems >= 10: return "PRO", ACCENT_COLOR, "#000000"
    return "BEGINNER", "#2a2d36", TEXT_COLOR

def center_text(draw, text, font, x_center, y, fill):
    try:
        w = draw.textlength(text, font=font)
    except:
        w = len(text) * 15 # fallback approx
    draw.text((x_center - w/2, y), text, font=font, fill=fill)

def generate_profile_card(full_name, username, user_id, bio, rank, gems, searches, downloads, joined, avatar_path=None):
    # Compact layout for bigger relative text sizes (responsive!)
    width, height = 800, 440
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    # Avatar placement
    avatar_size = 170
    avatar_x, avatar_y = 50, 60
    _draw_avatar(img, avatar_path, avatar_x, avatar_y, avatar_size)
    
    text_x = 260
    
    # Badge Box
    badge_text, badge_color, badge_text_c = get_badge_title(gems, rank)
    draw.rounded_rectangle([text_x, 60, text_x + 100, 85], radius=6, fill=badge_color)
    center_text(draw, badge_text, fonts['badge'], text_x + 50, 62, badge_text_c)
    
    # Global Rank (Top Right)
    rank_str = f"#{rank}"
    draw.text((width - 120, 60), "RANK", font=fonts['small'], fill=SUB_TEXT_COLOR)
    draw.text((width - 120, 75), rank_str, font=fonts['title'], fill=HIGHLIGHT_COLOR)
    
    # Name
    safe_name = full_name.upper()[:16]
    draw.text((text_x, 100), safe_name, font=fonts['name'], fill=TEXT_COLOR)
    
    # Username handle
    handle = f"@{username}  •  ID: {user_id}"
    draw.text((text_x, 155), handle, font=fonts['handle'], fill=SUB_TEXT_COLOR)
    
    # --- UI Grid layout instead of a faulty line ---
    box_y = 210
    box_w, box_h = 220, 110
    
    def draw_stat_box(bx, by, label, value):
        draw.rounded_rectangle([bx, by, bx+box_w, by+box_h], radius=15, fill="#232630")
        center_text(draw, str(value), fonts['stats_num'], bx + box_w/2, by + 20, TEXT_COLOR)
        center_text(draw, label.upper(), fonts['small'], bx + box_w/2, by + 70, ACCENT_COLOR)
    
    gap = 20
    draw_stat_box(50, box_y, "Gems", gems)
    draw_stat_box(50 + box_w + gap, box_y, "Searches", searches)
    draw_stat_box(50 + (box_w + gap)*2, box_y, "Downloads", downloads)
    
    # Bottom Bar
    lvl = (gems // 10) + 1
    xp = gems % 10
    total_xp_bar = "━" * xp + "┄" * (10 - xp)
    draw.text((50, 360), f"LEVEL {lvl}   {total_xp_bar}  {xp}/10 XP", font=fonts['badge'], fill=ACCENT_COLOR)
    draw.text((width - 200, 365), f"Joined: {joined}", font=fonts['handle'], fill=SUB_TEXT_COLOR)
    
    output_path = f"profile_{user_id}.png"
    img.save(output_path)
    return output_path

def generate_leaderboard_card(users):
    width = 800
    row_height = 80
    header_height = 120
    height = header_height + (len(users) * row_height) + 50
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((50, 45), "🏆 GLOBAL LEADERBOARD", font=fonts['name'], fill=ACCENT_COLOR)
    
    y = header_height + 10
    for i, u in enumerate(users, 1):
        color = RANK_COLORS.get(i, TEXT_COLOR)
        name = u.get('first_name', 'Unknown')
        points = u.get('points', 0)
        
        draw.text((50, y), f"#{i}", font=fonts['title'], fill=color)
        draw.text((130, y), name[:15], font=fonts['title'], fill=TEXT_COLOR)
        
        score_text = f"{points} GEMS"
        draw.text((580, y), score_text, font=fonts['title'], fill=ACCENT_COLOR)
        
        y += row_height
        
    output_path = "leaderboard_card.png"
    img.save(output_path)
    return output_path

def generate_top_searches_card(searches):
    width = 800
    row_height = 80
    header_height = 120
    height = header_height + (len(searches) * row_height) + 50
    if height < 400: height = 400
    
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((50, 45), "🔥 TRENDING NOW", font=fonts['name'], fill=ACCENT_COLOR)
    
    y = header_height + 10
    for i, s in enumerate(searches, 1):
        query = s['query'].upper()[:20]
        count = s['count']
        
        draw.text((50, y), f"{i}.", font=fonts['title'], fill=SUB_TEXT_COLOR)
        draw.text((120, y), query, font=fonts['title'], fill=TEXT_COLOR)
        draw.text((630, y), f"{count} 🔥", font=fonts['title'], fill=HIGHLIGHT_COLOR)
        
        y += row_height
        
    output_path = "top_searches_card.png"
    img.save(output_path)
    return output_path

def generate_stats_card(stats):
    width, height = 800, 440
    img, draw = create_base_canvas(width, height)
    fonts = get_fonts()
    
    draw.text((50, 50), "📊 SYSTEM INTELLIGENCE", font=fonts['name'], fill=ACCENT_COLOR)
    
    # Big Stat Boxes
    box_y = 150
    box_w, box_h = 220, 130
    
    def draw_sys_box(bx, by, label, value):
        draw.rounded_rectangle([bx, by, bx+box_w, by+box_h], radius=15, fill="#232630")
        center_text(draw, str(value), fonts['name'], bx + box_w/2, by + 25, TEXT_COLOR)
        center_text(draw, label.upper(), fonts['badge'], bx + box_w/2, by + 85, ACCENT_COLOR)
        
    gap = 20
    draw_sys_box(50, box_y, "Users", f"{stats.get('users', 0):,}+")
    draw_sys_box(50 + box_w + gap, box_y, "Files", f"{stats.get('files', 0):,}+")
    draw_sys_box(50 + (box_w + gap)*2, box_y, "Searches", f"{stats.get('searches', 0):,}+")
    
    draw.text((50, 360), "Status: 🟢 ONLINE   |   Network Latency: <30ms", font=fonts['handle'], fill=SUB_TEXT_COLOR)
    
    output_path = "stats_card.png"
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    generate_profile_card("KURUP LAST", "kurup_xd", 1234567, "Bio", 1, 154, 45, 12, "20 Mar 2026")
    generate_leaderboard_card([{"first_name": "Kurup", "points": 154}, {"first_name": "Alice", "points": 80}])
    generate_top_searches_card([{"query": "Inception", "count": 1500}, {"query": "Interstellar", "count": 1200}])
    generate_stats_card({"users": 15000, "files": 450000, "searches": 900000})
