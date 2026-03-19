import re

# Cleaning patterns
JUNK_WORDS = [
    r'prmovies', r'hdhub', r'mkvking', r'1xbet', r'downloadhub', r'bolly4u', r'moviesflix', r'desiremovies',
    r'tamilyogi', r'tamilrockers', r'khatrimaza', r'worldfree4u', r'filmyzilla', r'com', r'org', r'net',
    r'x264', r'x265', r'hevc', r'brrip', r'bdrip', r'bluray', r'webrip', r'h264', r'h265', r'encoded', r'by'
]

QUALITY_PATTERNS = [
    r'2160p', r'1080p', r'720p', r'480p', r'360p', r'4k', r'CAMRip', r'HDRip', r'WEB-DL', r'BluRay'
]

LANGUAGES = [
    'Hindi', 'English', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Marathi', 'Punjabi', 'Dual', 'Multi'
]

def clean_text(text: str, remove_junk: bool = True) -> str:
    """Removes junk words, extensions, and replaces separators with spaces."""
    if not text:
        return ""
    
    # Remove extension
    text = re.sub(r'\.(mp4|mkv|avi|m4v|ts)$', '', text, flags=re.I)
    
    # Remove all content inside brackets (often contains junk)
    text = re.sub(r'[\[\]\(\)]', ' ', text)
    
    # Replace separators with space
    text = re.sub(r'[\._\-]', ' ', text)
    
    # Remove junk words if requested
    if remove_junk:
        for word in JUNK_WORDS:
            text = re.sub(rf'\b{word}\b', '', text, flags=re.I)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_movie_data(text: str):
    """
    Extracts movie name, year, quality, and language from text.
    Returns a dict with cleaned data.
    """
    if not text:
        return None

    # Step 1: Preliminary cleaning (separators, brackets, but keep words)
    text = clean_text(text, remove_junk=False)
    
    # 1. Extract Year (4 digits starting with 19 or 20)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    year = year_match.group(1) if year_match else None
    if year_match:
        text = re.sub(rf'\b{year}\b', ' ', text)

    # 2. Extract Quality (Loop through all and remove them from text)
    quality = "Unknown"
    for q in QUALITY_PATTERNS:
        if re.search(rf'\b{q}\b', text, re.I):
            if quality == "Unknown":
                quality = q
            text = re.sub(rf'\b{q}\b', ' ', text, flags=re.I)

    # 3. Extract Language (Remove all found languages from text)
    found_langs = []
    for lang in LANGUAGES:
        if re.search(rf'\b{lang}\b', text, re.I):
            found_langs.append(lang)
            text = re.sub(rf'\b{lang}\b', ' ', text, flags=re.I)
    
    language = ", ".join(found_langs) if found_langs else "Unknown"

    # 4. Final Clean (remove junk words and extra spaces)
    movie_name = clean_text(text, remove_junk=True)
    
    # Final Movie Key (name + year)
    movie_key = f"{movie_name.lower()} {year}" if year else movie_name.lower()
    
    return {
        "movie_name": movie_name,
        "year": year,
        "quality": quality,
        "movie_language": language,
        "movie_key": movie_key.strip()
    }

if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Prmovies-Subedaar_Hindi_720p.mp4", "Subedaar (2026) [1080p] [Hindi]"),
        ("Filmyzilla.com-Animal_2023_Hindi_HDRip.mkv", None),
        ("Khatrimaza_The_Dark_Knight_2008_720p_Dual_Audio.mp4", "The Dark Knight 2008 1080p Bluray")
    ]
    
    for filename, caption in test_cases:
        print(f"Testing: {filename} | {caption}")
        # Prioritize caption
        result = parse_movie_data(caption) if caption else parse_movie_data(filename)
        print(f"Result: {result}\n")
