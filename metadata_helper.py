from imdb import Cinemagoer
import asyncio
import logging

logger = logging.getLogger(__name__)
ia = Cinemagoer()

async def get_movie_metadata(query: str, year: int = None):
    """
    Fetches movie metadata (poster, plot, rating) from IMDb using Cinemagoer.
    This is done in a thread pool as cinemagoer is synchronous.
    """
    loop = asyncio.get_event_loop()
    try:
        # Search for the movie
        search_results = await loop.run_in_executor(None, ia.search_movie, query)
        if not search_results:
            return None
        
        # Try to find the best match (considering year if provided)
        movie = None
        if year:
            for result in search_results:
                if result.get('year') == year:
                    movie = result
                    break
        
        if not movie:
            movie = search_results[0]
            
        # Fetch full details
        await loop.run_in_executor(None, ia.update, movie, ['main', 'plot'])
        
        poster = movie.get('full-size cover url')
        plot = movie.get('plot', ['No plot available.'])[0].split('::')[0]
        rating = movie.get('rating', 'N/A')
        title = movie.get('title', query)
        year = movie.get('year', 'Unknown')
        
        return {
            "title": title,
            "year": year,
            "poster": poster,
            "plot": plot,
            "rating": rating
        }
    except Exception as e:
        logger.error(f"Error fetching metadata for {query}: {e}")
        return None
