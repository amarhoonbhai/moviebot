import re

JUNK_WORDS = [
    r'prmovies', r'hdhub', r'mkvking', r'1xbet', r'downloadhub', r'bolly4u', r'moviesflix', r'desiremovies',
    r'tamilyogi', r'tamilrockers', r'khatrimaza', r'worldfree4u', r'filmyzilla', r'com', r'org', r'net',
    r'encoded', r'by', r'torrent', r'yts', r'hdrip', r'webrip', r'brrip', r'hdcam', r'camrip', r'dvdscr', r'x264', r'x265', r'hevc'
]

def parse_movie_data(text: str):
    if not text: return None
    
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    year = year_match.group(1) if year_match else None
    
    quality_match = re.search(r'\b(2160p|1080p|720p|480p|360p|4k|CAMRip|HDRip|WEB-DL|BluRay)\b', text, re.I)
    quality = quality_match.group(1).upper() if quality_match else "Unknown"
    
    languages = []
    for lang in ['Hindi', 'English', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Marathi', 'Punjabi', 'Dual', 'Multi']:
        if re.search(rf'\b{lang}\b', text, re.I):
            languages.append(lang)
    language = ", ".join(languages) if languages else "Unknown"
    
    clean_name = text
    clean_name = re.sub(r'\.(mp4|mkv|avi|m4v|ts)$', ' ', clean_name, flags=re.I)
    clean_name = re.sub(r'[\[\]\(\)\._\-]', ' ', clean_name)
    
    if year: clean_name = re.sub(rf'\b{year}\b', ' ', clean_name)
    if quality_match: clean_name = re.sub(rf'\b{quality_match.group(1)}\b', ' ', clean_name, flags=re.I)
    for lang in languages: clean_name = re.sub(rf'\b{lang}\b', ' ', clean_name, flags=re.I)
    
    for word in JUNK_WORDS:
        clean_name = re.sub(rf'\b{word}\b', ' ', clean_name, flags=re.I)
        
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    
    return {
        "movie_name": clean_name,
        "year": year,
        "quality": quality,
        "language": language
    }
