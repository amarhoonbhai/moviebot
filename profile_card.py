from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def generate_profile_card(name, rank, gems, searches, downloads, joined):
    """Generates a premium statistics card for the user."""
    
    # Card Dimensions
    width, height = 800, 450
    
    # Create background with gradient
    image = Image.new("RGB", (width, height), "#1a1a2e")
    draw = ImageDraw.Draw(image)
    
    # Simple Gradient Effect
    for i in range(height):
        r = int(26 + (i / height) * 20)
        g = int(26 + (i / height) * 10)
        b = int(46 + (i / height) * 30)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Try to load a font, fallback to default
    try:
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        title_font = ImageFont.truetype(font_path, 45)
        name_font = ImageFont.truetype(font_path, 35)
        stats_font = ImageFont.truetype(font_path, 28)
        label_font = ImageFont.truetype(font_path, 20)
    except:
        title_font = name_font = stats_font = label_font = ImageFont.load_default()

    # Draw Title
    draw.text((40, 40), "PREMIUM USER PROFILE", font=title_font, fill="#ffcc00")
    draw.line([(40, 100), (350, 100)], fill="#ffcc00", width=3)

    # Draw Name
    draw.text((40, 120), f"👤 {name.upper()}", font=name_font, fill="#ffffff")

    # Stats Blocks
    def draw_stat(x, y, label, value, color="#ffffff"):
        # Draw small block
        draw.rectangle([x, y, x+220, y+100], outline="#444466", width=2)
        draw.text((x+20, y+20), label, font=label_font, fill="#aaaaaa")
        draw.text((x+20, y+50), str(value), font=stats_font, fill=color)

    # First Row
    draw_stat(40, 190, "GLOBAL RANK", f"#{rank}", "#00ffcc")
    draw_stat(280, 190, "TOTAL GEMS", f"{gems} 💎", "#ffdd00")
    draw_stat(520, 190, "SINCE", joined, "#ffffff")

    # Second Row
    draw_stat(40, 310, "SEARCHES", searches, "#ffffff")
    draw_stat(280, 310, "DOWNLOADS", downloads, "#ffffff")
    
    # Footer
    draw.text((600, 400), "PRO MOVIE BOT v4.0", font=label_font, fill="#444466")
    
    # Save to temp file
    output_path = f"profile_{name}.png"
    image.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test generation
    generate_profile_card("Philobott", 1, 1500, 45, 12, "20 Mar 2026")
    print("Test card generated!")
