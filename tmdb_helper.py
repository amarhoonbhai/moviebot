import aiohttp
import asyncio
import logging
from config import TMDB_API_KEY
from database import db

logger = logging.getLogger(__name__)

async def get_movie_details(query: str, year: int | str | None = None):
    """Fetches movie metadata from TMDB with caching."""
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY not found in config.")
        return None

    # Check Cache
    cached_data = await db.get_tmdb_cache(query, str(year) if year else None)
    if cached_data:
        return cached_data

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
                    return None
                
                data = await response.json()
                if not data.get("results"):
                    return None
                
                # Best match
                movie = data["results"][0]
                movie_id = movie["id"]
                
                # Fetch full details (for better rating/poster)
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                async with session.get(details_url, params={"api_key": TMDB_API_KEY, "append_to_response": "credits"}) as details_resp:
                    if details_resp.status == 200:
                        movie = await details_resp.json()

                poster_path = movie.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else None
                
                # Extended Metadata
                credits = movie.get("credits", {})
                cast_list = credits.get("cast", [])
                cast = ", ".join([c["name"] for c in cast_list[:3]]) if cast_list else "Unknown"

                crew_list = credits.get("crew", [])
                directors = [c["name"] for c in crew_list if c.get("job") == "Director"]
                director = directors[0] if directors else "Unknown"
                
                genres_list = movie.get("genres", [])
                genres = ", ".join([g["name"] for g in genres_list[:3]]) if genres_list else "Unknown"
                
                runtime = movie.get("runtime", 0)
                if not runtime: runtime = "N/A"
                else: runtime = f"{runtime} min"
                
                result = {
                    "title": movie.get("title", query),
                    "year": str(movie.get("release_date", "0000"))[:4],
                    "rating": str(movie.get("vote_average", "N/A"))[:3],
                    "poster": poster_url,
                    "plot": movie.get("overview", "No plot available."),
                    "genres": genres,
                    "runtime": runtime,
                    "cast": cast,
                    "director": director
                }
                
                await db.save_tmdb_cache(query, str(year) if year else None, result)
                return result
    except Exception as e:
        logger.error(f"Error fetching TMDB data for {query}: {e}")
        return None
