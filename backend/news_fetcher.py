import feedparser
import httpx
import asyncio
import logging
import hashlib
from datetime import datetime
from sqlalchemy import select
from models import RawNews, Category
from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Direct quality news sources (NO Google News aggregator)
RSS_SOURCES = {
    "technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.wired.com/feed/rss",
        "https://feeds.thehackernews.com/feed",
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
        "https://www.espncricinfo.com/rss/content/story/feeds/cricket",
        "https://feeds.skysports.com/feeds/rss/football.xml",
    ],
    "business": [
        "https://feeds.feedburner.com/entrepreneur/latest",
        "https://www.moneycontrol.com/rss/business.xml",
        "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "https://feeds.bloomberg.com/markets/news/feed.rss",
    ],
    "entertainment": [
        "https://www.pinkvilla.com/feed",
        "https://feeds.bollywoodhungama.com/rss",
        "https://www.deccanchronicle.com/feeds",
    ],
    "education": [
        "https://feeds.aajtak.intoday.in/feeds/aajtak-education.xml",
        "https://feeds.theprint.in/education",
        "https://feeds.hindustantimes.com/feeds/education",
    ],
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://feeds.cnbc.com/feeds/world",
    ],
    "india": [
        "https://feeds.feedburner.com/ndtvnews-india-news",
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://feeds.hindustantimes.com/feeds/india",
        "https://feeds.aajtak.intoday.in/feeds/aajtak-national.xml",
    ],
    "general": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.apnews.com/apn/apnfeatures",
        "https://feeds.reuters.com/reuters/topNews",
    ]
}


def generate_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


async def fetch_rss_feed(url: str) -> list:
    """Fetch and parse RSS feed"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
        feed = feedparser.parse(response.text)
        articles = []
        
        for entry in feed.entries[:10]:
            title = entry.get("title", "").strip()
            description = entry.get("summary", "").strip()
            url_link = entry.get("link", "").strip()
            
            # Parse published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    published = datetime.utcnow()
            
            if title and url_link:
                articles.append({
                    "title": title[:500],
                    "description": description[:2000] if description else "",
                    "url": url_link[:1000],
                    "published_at": published or datetime.utcnow(),
                    "source": feed.feed.get("title", url)[:200]
                })
        
        return articles
        
    except Exception as e:
        logger.error(f"RSS Error {url}: {str(e)[:100]}")
        return []


async def save_news_to_db(articles: list, category_slug: str):
    """Save fetched news, skip duplicates"""
    saved_count = 0
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Category).where(Category.slug == category_slug)
            )
            category = result.scalar_one_or_none()
            
            for article in articles:
                # Check duplicate by URL
                existing = await session.execute(
                    select(RawNews).where(RawNews.url == article["url"])
                )
                if existing.scalar_one_or_none():
                    continue
                
                news = RawNews(
                    title=article["title"],
                    description=article["description"],
                    url=article["url"],
                    source=article["source"],
                    published_at=article["published_at"],
                    category_id=category.id if category else None,
                    is_processed=False
                )
                
                session.add(news)
                saved_count += 1
            
            await session.commit()
            logger.info(
                f"Saved {saved_count} articles for {category_slug}"
            )
            
        except Exception as e:
            await session.rollback()
            logger.error(f"DB Error: {e}")
    
    return saved_count


async def fetch_all_news():
    """Fetch news from all quality sources"""
    logger.info("News fetch started...")
    total_saved = 0
    
    tasks = []
    for category_slug, urls in RSS_SOURCES.items():
        for url in urls:
            tasks.append((url, category_slug))
    
    # Fetch all feeds
    results = await asyncio.gather(
        *[fetch_rss_feed(url) for url, _ in tasks],
        return_exceptions=True
    )
    
    # Group by category
    category_articles = {}
    for i, (url, category_slug) in enumerate(tasks):
        if isinstance(results[i], list):
            if category_slug not in category_articles:
                category_articles[category_slug] = []
            category_articles[category_slug].extend(results[i])
    
    # Save by category
    for category_slug, articles in category_articles.items():
        # Remove duplicates in batch
        seen_urls = set()
        unique = []
        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique.append(article)
        
        saved = await save_news_to_db(unique, category_slug)
        total_saved += saved
    
    logger.info(f"News fetch done! Total: {total_saved}")
    return total_saved


async def get_unprocessed_news(limit: int = 10) -> list:
    """Get unpublished news"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RawNews)
            .where(RawNews.is_processed == False)
            .order_by(RawNews.fetched_at.desc())
            .limit(limit)
        )
        news_list = result.scalars().all()
        
        return [
            {
                "id": news.id,
                "title": news.title,
                "description": news.description,
                "url": news.url,
                "source": news.source,
                "category_id": news.category_id,
                "published_at": news.published_at
            }
            for news in news_list
        ]


async def mark_news_processed(news_id: int):
    """Mark news as article"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(RawNews).where(RawNews.id == news_id)
            )
            news = result.scalar_one_or_none()
            if news:
                news.is_processed = True
                await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Mark error: {e}")
