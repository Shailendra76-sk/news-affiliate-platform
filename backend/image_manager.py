import os
import logging
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Category to search keywords mapping
CATEGORY_KEYWORDS = {
    "technology": [
        "technology", "computer", "smartphone", 
        "coding", "digital", "innovation"
    ],
    "sports": [
        "cricket", "sports", "football", 
        "athletics", "stadium", "team"
    ],
    "business": [
        "business", "finance", "office", 
        "meeting", "economy", "market"
    ],
    "entertainment": [
        "entertainment", "cinema", "music", 
        "bollywood", "festival", "celebration"
    ],
    "education": [
        "education", "books", "study", 
        "university", "learning", "school"
    ],
    "world": [
        "world", "globe", "international", 
        "travel", "culture", "city"
    ],
    "india": [
        "india", "delhi", "mumbai", 
        "indian culture", "temple", "taj mahal"
    ],
    "general": [
        "news", "newspaper", "media", 
        "information", "communication"
    ]
}


async def fetch_unsplash_image(query: str) -> dict:
    """Fetch image from Unsplash API"""
    if not UNSPLASH_ACCESS_KEY:
        return None
        
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.unsplash.com/photos/random",
                params={
                    "query": query,
                    "orientation": "landscape",
                    "content_filter": "high"
                },
                headers={
                    "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "url": data["urls"]["regular"],
                "thumb": data["urls"]["thumb"],
                "full": data["urls"]["full"],
                "alt": data.get("alt_description", query),
                "photographer": data["user"]["name"],
                "source": "unsplash"
            }
            
    except Exception as e:
        logger.error(f"Unsplash error: {e}")
        return None


async def fetch_pexels_image(query: str) -> dict:
    """Fetch image from Pexels API"""
    if not PEXELS_API_KEY:
        return None
        
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.pexels.com/v1/search",
                params={
                    "query": query,
                    "per_page": 5,
                    "orientation": "landscape"
                },
                headers={
                    "Authorization": PEXELS_API_KEY
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("photos"):
                photo = data["photos"][0]
                return {
                    "url": photo["src"]["large"],
                    "thumb": photo["src"]["medium"],
                    "full": photo["src"]["original"],
                    "alt": photo.get("alt", query),
                    "photographer": photo["photographer"],
                    "source": "pexels"
                }
                
    except Exception as e:
        logger.error(f"Pexels error: {e}")
        return None


async def get_fallback_image(category: str) -> dict:
    """Get fallback image URL when APIs fail"""
    
    fallback_images = {
        "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800",
        "business": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
        "entertainment": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800",
        "education": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
        "world": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5ce?w=800",
        "india": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800",
        "general": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"
    }
    
    url = fallback_images.get(category, fallback_images["general"])
    
    return {
        "url": url,
        "thumb": url,
        "full": url,
        "alt": f"{category} news",
        "photographer": "Unsplash",
        "source": "fallback"
    }


async def get_article_image(
    title: str, 
    category_slug: str = "general"
)
