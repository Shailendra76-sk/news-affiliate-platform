from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db, init_db
from models import (
    Article, Category, AffiliateProduct,
    FacebookPost, AIUsage, Analytics, RawNews
)
from news_fetcher import fetch_all_news
from article_generator import generate_articles_batch
from image_manager import attach_images_to_articles
from affiliate_engine import attach_affiliate_to_articles
from facebook_manager import run_facebook_automation
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="News Affiliate Platform API",
    description="Automated News + Affiliate Marketing Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# STARTUP
# ========================================

@app.on_event("startup")
async def startup():
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized!")


# ========================================
# HEALTH CHECK
# ========================================

# Yahan get ki jagah api_route use karke dono methods allow karein
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    return {
        "status": "running",
        "app": "News Affiliate Platform",
        "version": "1.0.0",
        "time": datetime.utcnow().isoformat()
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request):
    return {"status": "healthy"}



# ========================================
# ARTICLES API
# ========================================

@app.get("/api/articles")
async def get_articles(
    page: int = 1,
    limit: int = 10,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        offset = (page - 1) * limit
        query = select(Article).where(
            Article.is_published == True
        ).order_by(desc(Article.published_at))

        if category:
            cat_result = await db.execute(
                select(Category).where(Category.slug == category)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                query = query.where(Article.category_id == cat.id)

        # Total count
        count_query = select(func.count(Article.id)).where(
            Article.is_published == True
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get articles
        result = await db.execute(query.offset(offset).limit(limit))
        articles = result.scalars().all()

        return {
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "summary": a.summary,
                    "featured_image": a.featured_image,
                    "hashtags": a.hashtags,
                    "word_count": a.word_count,
                    "category_id": a.category_id,
                    "views": a.views,
                    "published_at": a.published_at.isoformat()
                    if a.published_at else None
                }
                for a in articles
            ]
        }

    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles/{slug}")
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Article).where(Article.slug == slug)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Update views
        article.views += 1
        await db.commit()

        # Get category
        category = None
        if article.category_id:
            cat_result = await db.execute(
                select(Category).where(Category.id == article.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                category = {"id": cat.id, "name": cat.name, "slug": cat.slug}

        # Get affiliate products
        products_result = await db.execute(
            select(AffiliateProduct).where(
                AffiliateProduct.article_id == article.id
            )
        )
        products = products_result.scalars().all()

        # Get related articles
        related_query = select(Article).where(
            Article.is_published == True,
            Article.id != article.id,
            Article.category_id == article.category_id
        ).order_by(desc(Article.published_at)).limit(4)
        related_result = await db.execute(related_query)
        related = related_result.scalars().all()

        import json
        faq_data = []
        if article.faq:
            try:
                faq_data = json.loads(article.faq)
            except:
                faq_data = []

        return {
            "success": True,
            "article": {
                "id": article.id,
                "title": article.title,
                "slug": article.slug,
                "content": article.content,
                "summary": article.summary,
                "meta_description": article.meta_description,
                "meta_keywords": article.meta_keywords,
                "featured_image": article.featured_image,
                "og_image": article.og_image,
                "faq": faq_data,
                "conclusion": article.conclusion,
                "hashtags": article.hashtags,
                "word_count": article.word_count,
                "views": article.views,
                "category": category,
                "published_at": article.published_at.isoformat()
                if article.published_at else None,
                "affiliate_products": [
                    {
                        "id": p.id,
                        "name": p.product_name,
                        "url": p.product_url,
                        "image": p.product_image,
                        "price": p.price,
                        "category": p.category
                    }
                    for p in products
                ],
                "related_articles": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "slug": r.slug,
                        "featured_image": r.featured_image,
                        "published_at": r.published_at.isoformat()
                        if r.published_at else None
                    }
                    for r in related
                ]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# CATEGORIES API
# ========================================

@app.get("/api/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Category))
        categories = result.scalars().all()

        return {
            "success": True,
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "slug": c.slug,
                    "description": c.description,
                    "icon": c.icon
                }
                for c in categories
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# SEARCH API
# ========================================

@app.get("/api/search")
async def search_articles(
    q: str,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    try:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search query too short"
            )

        offset = (page - 1) * limit

        result = await db.execute(
            select(Article).where(
                Article.is_published == True,
                Article.title.contains(q)
            ).order_by(desc(Article.published_at))
            .offset(offset).limit(limit)
        )
        articles = result.scalars().all()

        return {
            "success": True,
            "query": q,
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "summary": a.summary,
                    "featured_image": a.featured_image,
                    "published_at": a.published_at.isoformat()
                    if a.published_at else None
                }
                for a in articles
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# TRENDING & POPULAR API
# ========================================

@app.get("/api/trending")
async def get_trending(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Article).where(
                Article.is_published == True
            ).order_by(desc(Article.views)).limit(5)
        )
        articles = result.scalars().all()

        return {
            "success": True,
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "featured_image": a.featured_image,
                    "views": a.views,
                    "published_at": a.published_at.isoformat()
                    if a.published_at else None
                }
                for a in articles
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# ADMIN API
# ========================================

@app.get("/api/admin/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    try:
        # Total articles
        total_articles = await db.execute(
            select(func.count(Article.id))
        )

        # Published articles
        published = await db.execute(
            select(func.count(Article.id)).where(
                Article.is_published == True
            )
        )

        # Total views
        total_views = await db.execute(
            select(func.sum(Article.views))
        )

        # Facebook posts
        fb_posts = await db.execute(
            select(func.count(FacebookPost.id)).where(
                FacebookPost.is_posted == True
            )
        )

        # AI usage
        ai_usage = await db.execute(
            select(func.count(AIUsage.id)).where(
                AIUsage.success == True
            )
        )

        # Total affiliate clicks
        affiliate_clicks = await db.execute(
            select(func.sum(AffiliateProduct.clicks))
        )

        # Raw news count
        raw_news = await db.execute(
            select(func.count(RawNews.id))
        )

        return {
            "success": True,
            "stats": {
                "total_articles": total_articles.scalar() or 0,
                "published_articles": published.scalar() or 0,
                "total_views": total_views.scalar() or 0,
                "facebook_posts": fb_posts.scalar() or 0,
                "ai_requests": ai_usage.scalar() or 0,
                "affiliate_clicks": affiliate_clicks.scalar() or 0,
                "raw_news_fetched": raw_news.scalar() or 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# AUTOMATION TRIGGERS
# ========================================

@app.post("/api/automation/run")
async def run_automation():
    """Manual trigger for full automation cycle"""
    try:
        logger.info("Manual automation triggered!")

        # Step 1: Fetch news
        news_count = await fetch_all_news()

        # Step 2: Generate articles
        article_count = await generate_articles_batch(count=5)

        # Step 3: Attach images
        await attach_images_to_articles()

        # Step 4: Attach affiliate products
        await attach_affiliate_to_articles()

        # Step 5: Post to Facebook
        await run_facebook_automation()

        return {
            "success": True,
            "message": "Automation cycle complete!",
            "results": {
                "news_fetched": news_count,
                "articles_generated": article_count
            }
        }

    except Exception as e:
        logger.error(f"Automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/automation/fetch-news")
async def trigger_fetch_news():
    count = await fetch_all_news()
    return {"success": True, "news_fetched": count}


@app.post("/api/automation/generate-articles")
async def trigger_generate_articles(count: int = 5):
    generated = await generate_articles_batch(count=count)
    return {"success": True, "articles_generated": generated}


@app.post("/api/automation/facebook")
async def trigger_facebook():
    await run_facebook_automation()
    return {"success": True, "message": "Facebook automation done!"}


# ========================================
# AFFILIATE CLICK TRACKING
# ========================================

@app.get("/api/affiliate/click/{product_id}")
async def track_click(product_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(AffiliateProduct).where(
                AffiliateProduct.id == product_id
            )
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.clicks += 1
        await db.commit()

        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=product.product_url)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# SITEMAP
# ========================================

@app.get("/sitemap.xml")
async def sitemap(db: AsyncSession = Depends(get_db)):
    from fastapi.responses import Response

    result = await db.execute(
        select(Article).where(
            Article.is_published == True
        ).order_by(desc(Article.published_at)).limit(1000)
    )
    articles = result.scalars().all()

    app_url = os.getenv("APP_URL", "https://yourwebsite.com")

    urls = [f"""
    <url>
        <loc>{app_url}</loc>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>"""]

    for article in articles:
        urls.append(f"""
    <url>
        <loc>{app_url}/article/{article.slug}</loc>
        <lastmod>{article.published_at.strftime('%Y-%m-%d') 
                  if article.published_at else ''}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""

    return Response(
        content=sitemap_xml,
        media_type="application/xml"
    )


# ========================================
# ROBOTS.TXT
# ========================================

@app.get("/robots.txt")
async def robots():
    from fastapi.responses import PlainTextResponse
    app_url = os.getenv("APP_URL", "https://yourwebsite.com")

    content = f"""User-agent: *
Allow: /
Disallow: /api/admin/
Sitemap: {app_url}/sitemap.xml"""

    return PlainTextResponse(content=content)
