import logging
import json
import re
import asyncio
from datetime import datetime
from sqlalchemy import select
from models import Article, Category, AIUsage
from database import AsyncSessionLocal
from ai_manager import ai_manager
from news_fetcher import get_unprocessed_news, mark_news_processed

logger = logging.getLogger(__name__)


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"{slug[:80]}-{timestamp}"


def count_words(text: str) -> int:
    return len(text.split())


def clean_json_response(text: str) -> str:
    """Clean AI response to extract JSON"""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Find JSON object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end+1]
    return text


async def generate_article_prompt(news_title: str, 
                                   news_description: str, 
                                   category: str) -> str:
    """Create prompt for article generation"""
    
    return f"""
Tum ek expert Hindi/Hinglish news writer ho. Neeche diye gaye news ke baare mein ek 
comprehensive aur engaging article likho.

NEWS TITLE: {news_title}
NEWS DESCRIPTION: {news_description}
CATEGORY: {category}

INSTRUCTIONS:
1. Article Hindi aur Hinglish mix mein likho (Roman script + Devanagari mix)
2. 1000-1500 words ka article likho
3. Human-like writing style use karo, AI jaisa nahi lagna chahiye
4. Article informative, engaging aur SEO-optimized hona chahiye

RETURN ONLY THIS JSON FORMAT (no extra text):
{{
    "seo_title": "SEO optimized title in Hindi/Hinglish (60 chars max)",
    "meta_description": "Meta description in Hindi/Hinglish (155 chars max)",
    "slug_hint": "english-url-slug-3-5-words",
    "summary": "2-3 line featured summary in Hindi/Hinglish",
    "content": "Full article content in Hindi/Hinglish (1000-1500 words). Use proper paragraphs. Include subheadings with ## prefix.",
    "faq": [
        {{"question": "FAQ question 1 in Hindi", "answer": "Answer 1 in Hindi"}},
        {{"question": "FAQ question 2 in Hindi", "answer": "Answer 2 in Hindi"}},
        {{"question": "FAQ question 3 in Hindi", "answer": "Answer 3 in Hindi"}}
    ],
    "conclusion": "Conclusion paragraph in Hindi/Hinglish (100-150 words)",
    "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5",
    "keywords": "keyword1, keyword2, keyword3, keyword4, keyword5"
}}
"""


async def save_ai_usage(provider: str, model: str, task_type: str, 
                         success: bool, response_time: float, 
                         error: str = None):
    """Save AI usage stats to database"""
    async with AsyncSessionLocal() as session:
        try:
            usage = AIUsage(
                provider=provider,
                model=model,
                task_type=task_type,
                success=success,
                response_time=response_time,
                error_message=error
            )
            session.add(usage)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving AI usage: {e}")


async def generate_single_article(news_item: dict) -> bool:
    """Generate one article from news item"""
    
    try:
        # Get category name
        category_name = "General"
        async with AsyncSessionLocal() as session:
            if news_item.get("category_id"):
                result = await session.execute(
                    select(Category).where(
                        Category.id == news_item["category_id"]
                    )
                )
                cat = result.scalar_one_or_none()
                if cat:
                    category_name = cat.name

        # Generate prompt
        prompt = await generate_article_prompt(
            news_item["title"],
            news_item.get("description", ""),
            category_name
        )

        # Call AI with fallback
        result = await ai_manager.generate(prompt, task_type="article")
        
        # Save AI usage
        await save_ai_usage(
            provider=result["provider"],
            model=result["model"],
            task_type="article_generation",
            success=result["success"],
            response_time=result.get("response_time", 0)
        )

        if not result["success"]:
            logger.error("All AI providers failed for article generation!")
            return False

        # Parse JSON response
        try:
            clean_response = clean_json_response(result["content"])
            article_data = json.loads(clean_response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Response was: {result['content'][:500]}")
            return False

        # Prepare FAQ as JSON string
        faq_json = json.dumps(
            article_data.get("faq", []), 
            ensure_ascii=False
        )

        # Generate slug
        slug_hint = article_data.get("slug_hint", "")
        if not slug_hint:
            slug_hint = news_item["title"]
        slug = generate_slug(slug_hint)

        # Count words
        content = article_data.get("content", "")
        word_count = count_words(content)

        # Save article to database
        async with AsyncSessionLocal() as session:
            try:
                article = Article(
                    title=article_data.get("seo_title", news_item["title"]),
                    slug=slug,
                    content=content,
                    summary=article_data.get("summary", ""),
                    meta_description=article_data.get("meta_description", ""),
                    meta_keywords=article_data.get("keywords", ""),
                    faq=faq_json,
                    conclusion=article_data.get("conclusion", ""),
                    hashtags=article_data.get("hashtags", ""),
                    language="hi",
                    ai_provider=result["provider"],
                    word_count=word_count,
                    is_published=True,
                    published_at=datetime.utcnow(),
                    category_id=news_item.get("category_id"),
                    raw_news_id=news_item["id"]
                )

                session.add(article)
                await session.commit()
                await session.refresh(article)
                
                logger.info(
                    f"Article saved: {article.title[:50]}... "
                    f"({word_count} words, {result['provider']})"
                )
                
                # Mark news as processed
                await mark_news_processed(news_item["id"])
                
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving article: {e}")
                return False

    except Exception as e:
        logger.error(f"Error generating article: {e}")
        return False


async def generate_articles_batch(count: int = 5) -> int:
    """Generate multiple articles in one cycle"""
    logger.info(f"Starting article generation batch (count: {count})")
    
    # Get unprocessed news
    news_list = await get_unprocessed_news(limit=count)
    
    if not news_list:
        logger.info("No unprocessed news found!")
        return 0
    
    success_count = 0
    
    for news_item in news_list:
        try:
            # Add delay between requests to avoid rate limits
            await asyncio.sleep(2)
            
            success = await generate_single_article(news_item)
            if success:
                success_count += 1
                logger.info(f"Article {success_count}/{len(news_list)} generated!")
            else:
                logger.warning(f"Failed to generate article for: {news_item['title'][:50]}")
                
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            continue
    
    logger.info(
        f"Batch complete! Generated {success_count}/{len(news_list)} articles"
    )
    return success_count


async def get_latest_articles(limit: int = 10, 
                               category_slug: str = None) -> list:
    """Get latest published articles"""
    async with AsyncSessionLocal() as session:
        query = select(Article).where(
            Article.is_published == True
        ).order_by(Article.published_at.desc()).limit(limit)
        
        if category_slug:
            result = await session.execute(
                select(Category).where(Category.slug == category_slug)
            )
            category = result.scalar_one_or_none()
            if category:
                query = select(Article).where(
                    Article.is_published == True,
                    Article.category_id == category.id
                ).order_by(Article.published_at.desc()).limit(limit)
        
        result = await session.execute(query)
        articles = result.scalars().all()
        
        return [
            {
                "id": a.id,
                "title": a.title,
                "slug": a.slug,
                "summary": a.summary,
                "featured_image": a.featured_image,
                "hashtags": a.hashtags,
                "word_count": a.word_count,
                "category_id": a.category_id,
                "published_at": a.published_at.isoformat() 
                                if a.published_at else None,
                "views": a.views
            }
            for a in articles
        ]
