import aiohttp
import asyncio
import logging
from config import TMDB_API_KEY

logger = logging.getLogger(__name__)

async def get_movie_details(query: str, year: int | str | None = None):
    """Fetches movie metadata from TMDB."""
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY not found in config.")
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
    }
    if year:
        params["year"] = year

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"TMDB API error: {response.status}")
                    return None
                
                data = await response.json()
                if not data.get("results"):
                    return None
                
                # Best match
                movie = data["results"][0]
                movie_id = movie["id"]
                
                # Fetch full details (for better rating/poster)
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                async with session.get(details_url, params={"api_key": TMDB_API_KEY}) as details_resp:
                    if details_resp.status == 200:
                        movie = await details_resp.json()

                poster_path = movie.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else None
                
                return {
                    "title": movie.get("title", query),
                    "year": movie.get("release_date", "0000")[:4],
                    "rating": movie.get("vote_average", "N/A"),
                    "poster": poster_url,
                    "plot": movie.get("overview", "No plot available.")
                }
    except Exception as e:
        logger.error(f"Error fetching TMDB data for {query}: {e}")
        return None
