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
APP_URL = os.getenv("APP_URL", "https://news-affiliate-platform.vercel.app")
WHATSAPP_CHANNEL = "https://www.whatsapp.com/channel/0029VbCy92nBadmau8nw0v3j"
AMAZON_TAG = "sk200709-21"

# Trending products for Facebook posts
TRENDING_PRODUCTS = [
    {
        "name": "Samsung Galaxy S24 Ultra",
        "price": "₹1,29,999",
        "url": f"https://www.amazon.in/s?k=Samsung+Galaxy+S24+Ultra&tag={AMAZON_TAG}",
        "emoji": "📱"
    },
    {
        "name": "Apple iPhone 15",
        "price": "₹79,999",
        "url": f"https://www.amazon.in/s?k=Apple+iPhone+15&tag={AMAZON_TAG}",
        "emoji": "📱"
    },
    {
        "name": "boAt Airdopes 141",
        "price": "₹1,299",
        "url": f"https://www.amazon.in/s?k=boAt+Airdopes+141&tag={AMAZON_TAG}",
        "emoji": "🎧"
    },
    {
        "name": "Amazon Echo Dot 5th Gen",
        "price": "₹4,999",
        "url": f"https://www.amazon.in/s?k=Echo+Dot+5th+Gen&tag={AMAZON_TAG}",
        "emoji": "🔊"
    },
    {
        "name": "Kindle Paperwhite",
        "price": "₹13,999",
        "url": f"https://www.amazon.in/s?k=Kindle+Paperwhite&tag={AMAZON_TAG}",
        "emoji": "📚"
    },
    {
        "name": "OnePlus Nord CE 3",
        "price": "₹24,999",
        "url": f"https://www.amazon.in/s?k=OnePlus+Nord+CE+3&tag={AMAZON_TAG}",
        "emoji": "📱"
    },
    {
        "name": "Mi Smart Band 8",
        "price": "₹3,499",
        "url": f"https://www.amazon.in/s?k=Mi+Smart+Band+8&tag={AMAZON_TAG}",
        "emoji": "⌚"
    },
    {
        "name": "Philips Air Fryer",
        "price": "₹7,995",
        "url": f"https://www.amazon.in/s?k=Philips+Air+Fryer&tag={AMAZON_TAG}",
        "emoji": "🍳"
    }
]


async def generate_article_fb_post(
    title: str,
    summary: str,
    category: str,
    article_url: str,
    hashtags: str
) -> str:
    """Generate professional article Facebook post"""

    prompt = f"""
You are a professional social media manager for IndiaXpress news platform.
Create an engaging Facebook post for this news article.

ARTICLE TITLE: {title}
SUMMARY: {summary}
CATEGORY: {category}
ARTICLE URL: {article_url}

REQUIREMENTS:
1. Write in English (Professional tone)
2. 150-200 words
3. Catchy opening line
4. 3-4 key highlights
5. Call to action to read full article
6. 5-6 relevant hashtags
7. Include article URL
8. Add WhatsApp channel: {WHATSAPP_CHANNEL}
9. Use 4-6 emojis
10. Professional newspaper style

RETURN ONLY THE POST TEXT.
"""

    result = await ai_manager.generate(prompt, task_type="facebook_article")

    if result["success"]:
        return result["content"]
    else:
        return f"""📰 Breaking News | IndiaXpress

{title}

{summary[:200]}...

🔗 Read Full Story: {article_url}

📲 Join our WhatsApp Channel for instant updates:
{WHATSAPP_CHANNEL}

{hashtags}
#IndiaXpress #BreakingNews #India"""


async def generate_trending_product_post(product_index: int = 0) -> str:
    """Generate trending product Facebook post"""

    product = TRENDING_PRODUCTS[product_index % len(TRENDING_PRODUCTS)]

    prompt = f"""
You are a deal hunter and product reviewer for IndiaXpress.
Create an engaging Facebook post for this trending Amazon product.

PRODUCT: {product['name']}
PRICE: {product['price']}
AMAZON LINK: {product['url']}

REQUIREMENTS:
1. Write in English
2. 100-150 words
3. Highlight why this product is trending
4. Mention key features (3-4 points)
5. Create urgency (limited offer feeling)
6. Include product link
7. Add WhatsApp channel link: {WHATSAPP_CHANNEL}
8. 4-5 relevant emojis
9. 4-5 hashtags

RETURN ONLY THE POST TEXT.
"""

    result = await ai_manager.generate(prompt, task_type="facebook_product")

    if result["success"]:
        return result["content"]
    else:
        return f"""{product['emoji']} Trending Deal Alert! | IndiaXpress

🔥 {product['name']}
💰 Best Price: {product['price']}

✅ Top rated product
✅ Fast delivery
✅ Best value for money

🛒 Buy Now on Amazon:
{product['url']}

📲 Follow us for more deals:
{WHATSAPP_CHANNEL}

#TrendingDeals #Amazon #IndiaXpress #BestPrice #Shopping"""


async def generate_news_fb_post(
    news_title: str,
    news_description: str,
    category: str,
    news_url: str
) -> str:
    """Generate professional news update post"""

    prompt = f"""
You are a news editor at IndiaXpress.
Create a breaking news Facebook post.

NEWS: {news_title}
DESCRIPTION: {news_description[:300]}
CATEGORY: {category}
SOURCE: {news_url}

REQUIREMENTS:
1. Write in English (Professional)
2. 100-150 words
3. Breaking news style
4. Key facts highlighted
5. Source link included
6. WhatsApp channel: {WHATSAPP_CHANNEL}
7. 4-5 emojis
8. 5-6 hashtags

RETURN ONLY THE POST TEXT.
"""

    result = await ai_manager.generate(prompt, task_type="facebook_news")

    if result["success"]:
        return result["content"]
    else:
        return f"""🚨 Breaking News | IndiaXpress

{news_title}

{news_description[:200]}...

🔗 Source: {news_url}

📲 Stay Updated - Join WhatsApp:
{WHATSAPP_CHANNEL}

#{category.title()}News #IndiaXpress #Breaking"""


async def post_to_facebook(
    message: str,
    image_url: str = None
) -> dict:
    """Post to Facebook Page"""

    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        logger.error("Facebook credentials missing!")
        return {"success": False, "error": "Credentials missing"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:

            if image_url:
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos",
                    data={
                        "message": message,
                        "url": image_url,
                        "access_token": FACEBOOK_ACCESS_TOKEN
                    }
                )
            else:
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
                return {"success": True, "post_id": data["id"]}
            else:
                return {"success": False, "error": str(data)}

    except httpx.HTTPStatusError as e:
        error_msg = f"Facebook API error: {e.response.text}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        logger.error(f"Facebook post error: {e}")
        return {"success": False, "error": str(e)}


async def save_fb_post(
    article_id=None,
    post_type="article",
    content="",
    image_url=None,
    hashtags="",
    fb_post_id=None,
    success=True,
    error=None
):
    """Save Facebook post to database"""
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
    """Post article to Facebook"""

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()

            if not article:
                return False

            if article.is_facebook_posted:
                return True

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

            article_url = f"{APP_URL}/article.html?slug={article.slug}"

            post_content = await generate_article_fb_post(
                title=article.title,
                summary=article.summary or "",
                category=category_name,
                article_url=article_url,
                hashtags=article.hashtags or ""
            )

            fb_result = await post_to_facebook(
                message=post_content,
                image_url=article.featured_image
            )

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
                article.is_facebook_posted = True
                await session.commit()
                logger.info(f"Article posted to Facebook: {article.title[:50]}")
                return True

            await session.commit()
            return False

        except Exception as e:
            await session.rollback()
            logger.error(f"Error posting article: {e}")
            return False


async def post_trending_product_to_facebook() -> bool:
    """Post trending product to Facebook"""
    try:
        # Rotate products based on hour
        product_index = datetime.now().hour % len(TRENDING_PRODUCTS)

        post_content = await generate_trending_product_post(product_index)

        product = TRENDING_PRODUCTS[product_index]

        fb_result = await post_to_facebook(
            message=post_content
        )

        await save_fb_post(
            post_type="product",
            content=post_content,
            fb_post_id=fb_result.get("post_id"),
            success=fb_result["success"],
            error=fb_result.get("error")
        )

        if fb_result["success"]:
            logger.info(
                f"Product posted to Facebook: {product['name']}"
            )
            return True

        return False

    except Exception as e:
        logger.error(f"Error posting product: {e}")
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

            post_content = await generate_news_fb_post(
                news_title=news.title,
                news_description=news.description or "",
                category=category_name,
                news_url=news.url
            )

            fb_result = await post_to_facebook(
                message=post_content
            )

            await save_fb_post(
                post_type="news",
                content=post_content,
                fb_post_id=fb_result.get("post_id"),
                success=fb_result["success"],
                error=fb_result.get("error")
            )

            return fb_result["success"]

        except Exception as e:
            logger.error(f"Error posting news: {e}")
            return False


async def run_facebook_automation():
    """
    Main Facebook automation:
    1. Post unpublished articles (with image)
    2. Post trending product
    3. Post latest news updates
    """
    logger.info("Starting Facebook automation...")

    posted_articles = 0
    posted_news = 0

    # 1. Post articles
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article).where(
                Article.is_published == True,
                Article.is_facebook_posted == False
            ).order_by(
                Article.published_at.desc()
            ).limit(3)
        )
        articles = result.scalars().all()

        for article in articles:
            await asyncio.sleep(5)
            success = await post_article_to_facebook(article.id)
            if success:
                posted_articles += 1
                logger.info(f"✅ Article: {article.title[:50]}")

    # 2. Post trending product (every other hour)
    if datetime.now().minute < 30:
        await asyncio.sleep(5)
        product_success = await post_trending_product_to_facebook()
        if product_success:
            logger.info("✅ Trending product posted!")

    # 3. Post news updates
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RawNews).where(
                RawNews.is_processed == False
            ).order_by(
                RawNews.fetched_at.desc()
            ).limit(3)
        )
        news_list = result.scalars().all()

        for news in news_list:
            await asyncio.sleep(5)
            success = await post_news_to_facebook(news.id)
            if success:
                posted_news += 1
                logger.info(f"✅ News: {news.title[:50]}")

    logger.info(
        f"Facebook done! Articles: {posted_articles}, "
        f"News: {posted_news}"
    )
