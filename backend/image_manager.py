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
) -> dict:
    """
    Main function - get best image for article
    Tries Unsplash first, then Pexels, then fallback
    """
    
    # Get search keywords for category
    keywords = CATEGORY_KEYWORDS.get(
        category_slug, 
        CATEGORY_KEYWORDS["general"]
    )
    
    # Extract keywords from title
    title_words = [
        word for word in title.split() 
        if len(word) > 4
    ][:3]
    
    # Build search query
    if title_words:
        query = " ".join(title_words)
    else:
        query = keywords[0]
    
    # Try Unsplash first
    image = await fetch_unsplash_image(query)
    if image:
        logger.info(f"Image from Unsplash: {query}")
        return image
    
    # Try category keyword if title query failed
    image = await fetch_unsplash_image(keywords[0])
    if image:
        logger.info(f"Image from Unsplash (category): {keywords[0]}")
        return image
    
    # Try Pexels
    image = await fetch_pexels_image(query)
    if image:
        logger.info(f"Image from Pexels: {query}")
        return image
    
    # Use fallback
    logger.warning(f"Using fallback image for: {category_slug}")
    return await get_fallback_image(category_slug)


async def update_article_image(article_id: int, category_slug: str, title: str):
    """Update article with fetched image"""
    from database import AsyncSessionLocal
    from models import Article
    from sqlalchemy import select
    
    image_data = await get_article_image(title, category_slug)
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()
            
            if article:
                article.featured_image = image_data["url"]
                article.og_image = image_data["url"]
                await session.commit()
                logger.info(f"Image updated for article {article_id}")
                return image_data
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating article image: {e}")
            return None


async def attach_images_to_articles():
    """Attach images to articles that don't have one"""
    from database import AsyncSessionLocal
    from models import Article, Category
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article).where(
                Article.featured_image == None,
                Article.is_published == True
            ).limit(20)
        )
        articles = result.scalars().all()
        
        logger.info(f"Attaching images to {len(articles)} articles...")
        
        for article in articles:
            try:
                # Get category slug
                category_slug = "general"
                if article.category_id:
                    cat_result = await session.execute(
                        select(Category).where(
                            Category.id == article.category_id
                        )
                    )
                    category = cat_result.scalar_one_or_none()
                    if category:
                        category_slug = category.slug
                
                await update_article_image(
                    article.id, 
                    category_slug, 
                    article.title
                )
                
                # Small delay to avoid API rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(
                    f"Error attaching image to article {article.id}: {e}"
                )
                continue
        
        logger.info("Image attachment complete!")
