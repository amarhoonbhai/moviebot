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
    try:
        cached_data = await asyncio.wait_for(db.get_tmdb_cache(query, str(year) if year else None), timeout=2.0)
        if cached_data:
            return cached_data
    except Exception:
        pass

    url = "https://api.themoviedb.org/3/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                results = data.get("results", [])
                if not results:
                    return None
                
                # Filter out persons, prefer movies/tv
                valid_results = [r for r in results if r.get("media_type") in ["movie", "tv"]]
                if not valid_results:
                    return None
                
                # Best match
                movie = valid_results[0]
                media_type = movie.get("media_type")
                movie_id = movie["id"]
                
                # Fetch full details
                details_url = f"https://api.themoviedb.org/3/{media_type}/{movie_id}"
                async with session.get(details_url, params={"api_key": TMDB_API_KEY, "append_to_response": "credits"}) as details_resp:
                    if details_resp.status == 200:
                        movie = await details_resp.json()

                poster_path = movie.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                
                # Extended Metadata
                credits = movie.get("credits", {})
                cast_list = credits.get("cast", [])
                cast = ", ".join([c["name"] for c in cast_list[:3]]) if cast_list else "Unknown"

                crew_list = credits.get("crew", [])
                directors = [c["name"] for c in crew_list if c.get("job") in ["Director", "Executive Producer"]]
                director = directors[0] if directors else "Unknown"
                
                genres_list = movie.get("genres", [])
                genres = ", ".join([g["name"] for g in genres_list[:3]]) if genres_list else "Unknown"
                
                if media_type == "movie":
                    runtime = movie.get("runtime", 0)
                    runtime = f"{runtime} min" if runtime else "N/A"
                    date_key = "release_date"
                    title_key = "title"
                    seasons = None
                else: # tv show
                    runtimes = movie.get("episode_run_time", [])
                    runtime = f"{runtimes[0]} min" if runtimes else "N/A"
                    date_key = "first_air_date"
                    title_key = "name"
                    seasons = movie.get("number_of_seasons")

                result = {
                    "title": movie.get(title_key, query),
                    "year": str(movie.get(date_key, "0000"))[:4],
                    "rating": str(movie.get("vote_average", "N/A"))[:3],
                    "poster": poster_url,
                    "plot": movie.get("overview", "No plot available."),
                    "genres": genres,
                    "runtime": runtime,
                    "cast": cast,
                    "director": director,
                    "seasons": seasons
                }
                
                try:
                    await asyncio.wait_for(db.save_tmdb_cache(query, str(year) if year else None, result), timeout=2.0)
                except:
                    pass
                return result
    except Exception as e:
        logger.error(f"Error fetching TMDB data for {query}: {e}")
        return None
