import os
import logging
import httpx
import asyncio
import random
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

# 🔥 Trending Products (hamesha fresh dikhne ke liye rotate honge)
TRENDING_PRODUCTS = [
    {"name": "Samsung Galaxy S24 Ultra", "price": "₹1,29,999", "emoji": "📱", 
     "url": f"https://www.amazon.in/s?k=Samsung+Galaxy+S24+Ultra&tag={AMAZON_TAG}"},
    {"name": "Apple iPhone 15", "price": "₹79,999", "emoji": "📱", 
     "url": f"https://www.amazon.in/s?k=Apple+iPhone+15&tag={AMAZON_TAG}"},
    {"name": "boAt Airdopes 141", "price": "₹1,299", "emoji": "🎧", 
     "url": f"https://www.amazon.in/s?k=boAt+Airdopes+141&tag={AMAZON_TAG}"},
    {"name": "Amazon Echo Dot 5th Gen", "price": "₹4,999", "emoji": "🔊", 
     "url": f"https://www.amazon.in/s?k=Echo+Dot+5th+Gen&tag={AMAZON_TAG}"},
    {"name": "Kindle Paperwhite", "price": "₹13,999", "emoji": "📚", 
     "url": f"https://www.amazon.in/s?k=Kindle+Paperwhite&tag={AMAZON_TAG}"},
    {"name": "OnePlus Nord CE 3", "price": "₹24,999", "emoji": "📱", 
     "url": f"https://www.amazon.in/s?k=OnePlus+Nord+CE+3&tag={AMAZON_TAG}"},
    {"name": "Mi Smart Band 8", "price": "₹3,499", "emoji": "⌚", 
     "url": f"https://www.amazon.in/s?k=Mi+Smart+Band+8&tag={AMAZON_TAG}"},
    {"name": "Philips Air Fryer", "price": "₹7,995", "emoji": "🍳", 
     "url": f"https://www.amazon.in/s?k=Philips+Air+Fryer&tag={AMAZON_TAG}"},
    {"name": "Realme Narzo 70 Pro", "price": "₹19,999", "emoji": "📱",
     "url": f"https://www.amazon.in/s?k=Realme+Narzo+70+Pro&tag={AMAZON_TAG}"},
    {"name": "Noise ColorFit Pro 5", "price": "₹2,499", "emoji": "⌚",
     "url": f"https://www.amazon.in/s?k=Noise+ColorFit+Pro+5&tag={AMAZON_TAG}"},
]

def get_trending_product():
    """Hamesha naya product – random choose karo"""
    return random.choice(TRENDING_PRODUCTS)

# ============================================
# FACEBOOK POST GENERATORS (NO SOURCE LINKS)
# ============================================

async def generate_article_fb_post(title, summary, category, article_url, hashtags):
    """Article post – sirf website + WhatsApp + product link"""
    product = get_trending_product()
    
    return f"""🔥 {title}

{summary[:180]}...

━━━━━━━━━━━━━━━━━━
🛒 TRENDING DEAL OF THE DAY
{product['emoji']} {product['name']}
💰 {product['price']}
👉 BUY NOW: {product['url']}
━━━━━━━━━━━━━━━━━━

📖 READ FULL ARTICLE:
{article_url}

📱 JOIN WHATSAPP CHANNEL:
{WHATSAPP_CHANNEL}

{hashtags}
#IndiaXpress #{category} #TrendingDeals"""


async def generate_news_fb_post(news_title, news_description, category):
    """Breaking news post – product + WhatsApp, no source link"""
    product = get_trending_product()
    
    return f"""⚡ BREAKING: {news_title}

{news_description[:150]}...

━━━━━━━━━━━━━━━━━━
🔥 TODAY'S HOT DEAL
{product['emoji']} {product['name']}
💰 {product['price']}
👉 SHOP: {product['url']}
━━━━━━━━━━━━━━━━━━

📱 MORE UPDATES ON WHATSAPP:
{WHATSAPP_CHANNEL}

#BreakingNews #{category} #IndiaXpress"""


async def generate_product_fb_post():
    """Sirf product post – trending product + WhatsApp"""
    product = get_trending_product()
    
    return f"""🔥 DEAL ALERT! {product['emoji']}

{product['name']}

💰 BEST PRICE: {product['price']}

✅ Top Rated
✅ Fast Delivery
✅ Limited Stock

👉 BUY NOW: {product['url']}

━━━━━━━━━━━━━━━━━━
📱 JOIN OUR WHATSAPP FOR MORE DEALS:
{WHATSAPP_CHANNEL}

#AmazonDeals #Trending #IndiaXpress"""

# ============================================
# POST TO FACEBOOK
# ============================================

async def post_to_facebook(message, image_url=None):
    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        logger.error("Facebook credentials missing!")
        return {"success": False, "error": "Missing credentials"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if image_url:
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos",
                    data={"message": message, "url": image_url, "access_token": FACEBOOK_ACCESS_TOKEN}
                )
            else:
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed",
                    data={"message": message, "access_token": FACEBOOK_ACCESS_TOKEN}
                )
            response.raise_for_status()
            data = response.json()
            if "id" in data:
                logger.info(f"FB post success! ID: {data['id']}")
                return {"success": True, "post_id": data["id"]}
            return {"success": False, "error": str(data)}
    except Exception as e:
        logger.error(f"FB error: {e}")
        return {"success": False, "error": str(e)}


async def save_fb_post(article_id=None, post_type="article", content="", image_url=None,
                       hashtags="", fb_post_id=None, success=True, error=None):
    async with AsyncSessionLocal() as session:
        try:
            fb_post = FacebookPost(
                article_id=article_id, post_type=post_type, content=content,
                image_url=image_url, hashtags=hashtags, fb_post_id=fb_post_id,
                is_posted=success, error_message=error,
                posted_at=datetime.utcnow() if success else None
            )
            session.add(fb_post)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Save error: {e}")

# ============================================
# MAIN POSTING FUNCTIONS
# ============================================

async def post_article_to_facebook(article_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Article).where(Article.id == article_id))
            article = result.scalar_one_or_none()
            if not article or article.is_facebook_posted:
                return False

            category_name = "General"
            if article.category_id:
                cat_res = await session.execute(select(Category).where(Category.id == article.category_id))
                cat = cat_res.scalar_one_or_none()
                if cat:
                    category_name = cat.name

            article_url = f"{APP_URL}/article.html?slug={article.slug}"
            post_content = await generate_article_fb_post(
                article.title, article.summary or "", category_name, article_url, article.hashtags or ""
            )
            fb_result = await post_to_facebook(post_content, article.featured_image)
            await save_fb_post(article_id, "article", post_content, article.featured_image,
                               article.hashtags or "", fb_result.get("post_id"), fb_result["success"], fb_result.get("error"))
            if fb_result["success"]:
                article.is_facebook_posted = True
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Article post error: {e}")
            return False


async def post_trending_product_to_facebook():
    try:
        post_content = await generate_product_fb_post()
        fb_result = await post_to_facebook(post_content)
        await save_fb_post(post_type="product", content=post_content,
                           fb_post_id=fb_result.get("post_id"), success=fb_result["success"], error=fb_result.get("error"))
        return fb_result["success"]
    except Exception as e:
        logger.error(f"Product post error: {e}")
        return False


async def post_news_to_facebook(news_id):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(RawNews).where(RawNews.id == news_id))
            news = result.scalar_one_or_none()
            if not news:
                return False

            category_name = "General"
            if news.category_id:
                cat_res = await session.execute(select(Category).where(Category.id == news.category_id))
                cat = cat_res.scalar_one_or_none()
                if cat:
                    category_name = cat.name

            post_content = await generate_news_fb_post(news.title, news.description or "", category_name)
            fb_result = await post_to_facebook(post_content)
            await save_fb_post(post_type="news", content=post_content,
                               fb_post_id=fb_result.get("post_id"), success=fb_result["success"], error=fb_result.get("error"))
            return fb_result["success"]
        except Exception as e:
            logger.error(f"News post error: {e}")
            return False

# ============================================
# MAIN AUTOMATION
# ============================================

async def run_facebook_automation():
    logger.info("Starting Facebook automation...")
    posted_articles = 0
    posted_news = 0

    # 1. Articles
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article).where(Article.is_published == True, Article.is_facebook_posted == False)
            .order_by(Article.published_at.desc()).limit(3)
        )
        articles = result.scalars().all()
        for art in articles:
            await asyncio.sleep(5)
            if await post_article_to_facebook(art.id):
                posted_articles += 1

    # 2. Product (har baar naya product)
    await asyncio.sleep(3)
    if await post_trending_product_to_facebook():
        logger.info("✅ Trending product posted!")

    # 3. News updates
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RawNews).where(RawNews.is_processed == False)
            .order_by(RawNews.fetched_at.desc()).limit(3)
        )
        news_list = result.scalars().all()
        for news in news_list:
            await asyncio.sleep(5)
            if await post_news_to_facebook(news.id):
                posted_news += 1

    logger.info(f"Facebook done! Articles: {posted_articles}, News: {posted_news}")
