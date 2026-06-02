import os
import logging
import httpx
import asyncio
import json
from datetime import datetime
from sqlalchemy import select
from models import Article, FacebookPost, Category, RawNews
from database import AsyncSessionLocal
from ai_manager import ai_manager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
APP_URL = os.getenv("APP_URL", "https://yourwebsite.com")


async def generate_fb_post_content(
    title: str,
    summary: str,
    category: str,
    hashtags: str,
    article_url: str
) -> str:
    """Generate engaging Facebook post using AI"""

    prompt = f"""
Tum ek social media expert ho. Neeche diye gaye article ke liye 
ek engaging Facebook post likho.

ARTICLE TITLE: {title}
ARTICLE SUMMARY: {summary}
CATEGORY: {category}
ARTICLE URL: {article_url}

INSTRUCTIONS:
1. Hindi/Hinglish mein likho
2. 150-200 words ka post
3. Engaging aur catchy opening line
4. 3-4 key points bullet points mein
5. Call to action (article padhne ke liye)
6. Emojis use karo (5-8)
7. End mein hashtags add karo: {hashtags}
8. Article URL include karo

RETURN ONLY THE POST TEXT, no extra explanation.
"""

    result = await ai_manager.generate(prompt, task_type="facebook_post")

    if result["success"]:
        return result["content"]
    else:
        # Fallback simple post
        return f"""
🔥 Breaking News! 

{title}

{summary}

📖 Poora article padhne ke liye link par click karein:
{article_url}

{hashtags}

#LatestNews #HindiNews #TrendingNow
"""


async def generate_news_fb_post(
    news_title: str,
    news_description: str,
    category: str,
    news_url: str
) -> str:
    """Generate Facebook post for raw news"""

    prompt = f"""
Tum ek news social media manager ho. Is breaking news ke liye 
ek short engaging Facebook post likho.

NEWS: {news_title}
DESCRIPTION: {news_description}
CATEGORY: {category}
SOURCE URL: {news_url}

INSTRUCTIONS:
1. Hindi/Hinglish mein likho
2. 100-150 words
3. Breaking news feel do
4. Important points highlight karo
5. 4-6 emojis use karo
6. Relevant hashtags add karo (5-6)
7. Source link include karo

RETURN ONLY THE POST TEXT.
"""

    result = await ai_manager.generate(prompt, task_type="news_fb_post")

    if result["success"]:
        return result["content"]
    else:
        return f"""
🚨 Breaking News!

{news_title}

{news_description[:200]}...

🔗 Source: {news_url}

#BreakingNews #HindiNews #{category.title()}News
"""


async def post_to_facebook_with_image(
    message: str,
    image_url: str = None
) -> dict:
    """Post to Facebook Page with optional image"""

    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        logger.error("Facebook credentials not configured!")
        return {"success": False, "error": "Credentials missing"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:

            if image_url:
                # Post with image
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos",
                    data={
                        "message": message,
                        "url": image_url,
                        "access_token": FACEBOOK_ACCESS_TOKEN
                    }
                )
            else:
                # Text only post
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed",
                    data={
                        "message": message,
                        "access_token": FACEBOOK_ACCESS_TOKEN
                    }
                )

            response.raise_for_status()
            data = response.json()

            if "id" in data:
                logger.info(f"Facebook post successful! ID: {data['id']}")
                return {
                    "success": True,
                    "post_id": data["id"]
                }
            else:
                return {
                    "success": False,
                    "error": str(data)
                }

    except httpx.HTTPStatusError as e:
        error_msg = f"Facebook API error: {e.response.text}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        logger.error(f"Facebook post error: {e}")
        return {"success": False, "error": str(e)}


async def save_fb_post(
    article_id: int = None,
    post_type: str = "article",
    content: str = "",
    image_url: str = None,
    hashtags: str = "",
    fb_post_id: str = None,
    success: bool = True,
    error: str = None
):
    """Save Facebook post record to database"""

    async with AsyncSessionLocal() as session:
        try:
            fb_post = FacebookPost(
                article_id=article_id,
                post_type=post_type,
                content=content,
                image_url=image_url,
                hashtags=hashtags,
                fb_post_id=fb_post_id,
                is_posted=success,
                error_message=error,
                posted_at=datetime.utcnow() if success else None
            )
            session.add(fb_post)
            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving FB post: {e}")


async def post_article_to_facebook(article_id: int) -> bool:
    """Post a published article to Facebook"""

    async with AsyncSessionLocal() as session:
        try:
            # Get article
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()

            if not article:
                logger.error(f"Article {article_id} not found!")
                return False

            if article.is_facebook_posted:
                logger.info(f"Article {article_id} already posted!")
                return True

            # Get category
            category_name = "General"
            if article.category_id:
                cat_result = await session.execute(
                    select(Category).where(
                        Category.id == article.category_id
                    )
                )
                category = cat_result.scalar_one_or_none()
                if category:
                    category_name = category.name

            # Generate article URL
            article_url = f"{APP_URL}/article/{article.slug}"

            # Generate FB post content
            post_content = await generate_fb_post_content(
                title=article.title,
                summary=article.summary or "",
                category=category_name,
                hashtags=article.hashtags or "",
                article_url=article_url
            )

            # Post to Facebook
            fb_result = await post_to_facebook_with_image(
                message=post_content,
                image_url=article.featured_image
            )

            # Save to database
            await save_fb_post(
                article_id=article_id,
                post_type="article",
                content=post_content,
                image_url=article.featured_image,
                hashtags=article.hashtags or "",
                fb_post_id=fb_result.get("post_id"),
                success=fb_result["success"],
                error=fb_result.get("error")
            )

            if fb_result["success"]:
                # Mark article as posted
                article.is_facebook_posted = True
                await session.commit()
                logger.info(
                    f"Article posted to Facebook: {article.title[:50]}"
                )
                return True
            else:
                await session.commit()
                return False

        except Exception as e:
            await session.rollback()
            logger.error(f"Error posting article to Facebook: {e}")
            return False


async def post_news_to_facebook(news_id: int) -> bool:
    """Post raw news to Facebook"""

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(RawNews).where(RawNews.id == news_id)
            )
            news = result.scalar_one_or_none()

            if not news:
                return False

            # Get category
            category_name = "General"
            if news.category_id:
                cat_result = await session.execute(
                    select(Category).where(
                        Category.id == news.category_id
                    )
                )
                category = cat_result.scalar_one_or_none()
                if category:
                    category_name = category.name

            # Generate FB post
            post_content = await generate_news_fb_post(
                news_title=news.title,
                news_description=news.description or "",
                category=category_name,
                news_url=news.url
            )

            # Post to Facebook
            fb_result = await post_to_facebook_with_image(
                message=post_content
            )

            # Save record
            await save_fb_post(
                post_type="news",
                content=post_content,
                fb_post_id=fb_result.get("post_id"),
                success=fb_result["success"],
                error=fb_result.get("error")
            )

            return fb_result["success"]

        except Exception as e:
            logger.error(f"Error posting news to Facebook: {e}")
            return False


async def run_facebook_automation():
    """
    Main automation function:
    1. Post unpublished articles to Facebook
    2. Post latest news to Facebook
    """
    logger.info("Starting Facebook automation...")

    # Post articles
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article).where(
                Article.is_published == True,
                Article.is_facebook_posted == False
            ).limit(5)
        )
        articles = result.scalars().all()

        for article in articles:
            await asyncio.sleep(3)
            success = await post_article_to_facebook(article.id)
            if success:
                logger.info(
                    f"✅ Article posted: {article.title[:50]}"
                )
            else:
                logger.warning(
                    f"❌ Failed to post: {article.title[:50]}"
                )

    # Post news
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RawNews).where(
                RawNews.is_processed == False
            ).order_by(
                RawNews.fetched_at.desc()
            ).limit(10)
        )
        news_list = result.scalars().all()

        posted_count = 0
        for news in news_list:
            if posted_count >= 5:
                break
            await asyncio.sleep(3)
            success = await post_news_to_facebook(news.id)
            if success:
                posted_count += 1
                logger.info(f"✅ News posted: {news.title[:50]}")

    logger.info("Facebook automation complete!")
