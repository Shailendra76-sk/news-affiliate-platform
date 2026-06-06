import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from news_fetcher import fetch_all_news
from article_generator import generate_articles_batch
from image_manager import attach_images_to_articles
from affiliate_engine import attach_affiliate_to_articles
from facebook_manager import run_facebook_automation
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

ARTICLES_PER_CYCLE = int(os.getenv("ARTICLES_PER_CYCLE", "5"))
WHATSAPP_CHANNEL = "https://www.whatsapp.com/channel/0029VbCy92nBadmau8nw0v3j"
AMAZON_TAG = "sk200709-21"


async def run_article_cycle():
    """
    Every 20 minutes:
    Fetch news → Generate articles → Images → Affiliate
    """
    now = datetime.now()
    hour = now.hour

    # Only run 6 AM to 10 PM
    if hour < 6 or hour >= 22:
        logger.info("Outside active hours (6AM-10PM). Skipping.")
        return

    start_time = datetime.utcnow()
    logger.info("=" * 50)
    logger.info(f"Article cycle started: {start_time}")
    logger.info("=" * 50)

    try:
        # Step 1: Fetch News
        logger.info("Step 1: Fetching news...")
        news_count = await fetch_all_news()
        logger.info(f"News fetched: {news_count}")

        await asyncio.sleep(5)

        # Step 2: Generate Articles
        logger.info("Step 2: Generating articles...")
        article_count = await generate_articles_batch(
            count=ARTICLES_PER_CYCLE
        )
        logger.info(f"Articles generated: {article_count}")

        await asyncio.sleep(3)

        # Step 3: Attach Images
        logger.info("Step 3: Attaching images...")
        await attach_images_to_articles()

        await asyncio.sleep(3)

        # Step 4: Attach Affiliate Products
        logger.info("Step 4: Attaching affiliate products...")
        await attach_affiliate_to_articles()

        end_time = datetime.utcnow()
        duration = (end_time - start_time).seconds

        logger.info("=" * 50)
        logger.info(f"Article cycle complete! Duration: {duration}s")
        logger.info(f"News: {news_count}, Articles: {article_count}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error in article cycle: {e}")


async def run_facebook_cycle():
    """
    Every hour 6 AM to 10 PM:
    Post articles + trending products to Facebook
    """
    now = datetime.now()
    hour = now.hour

    # Only run 6 AM to 10 PM
    if hour < 6 or hour >= 22:
        logger.info("Outside active hours. Skipping Facebook.")
        return

    logger.info("Starting Facebook automation cycle...")

    try:
        await run_facebook_automation()
        logger.info("Facebook cycle complete!")

    except Exception as e:
        logger.error(f"Facebook cycle error: {e}")


async def run_news_fetch_only():
    """Every 10 minutes - just fetch news"""
    try:
        count = await fetch_all_news()
        logger.info(f"Background news fetch: {count} articles")
    except Exception as e:
        logger.error(f"Background news fetch error: {e}")


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure scheduler"""
    scheduler = AsyncIOScheduler()

    # Articles every 20 minutes
    scheduler.add_job(
        run_article_cycle,
        trigger=IntervalTrigger(minutes=20),
        id="article_cycle",
        name="Article Generation - Every 20 Min",
        replace_existing=True,
        misfire_grace_time=300
    )

    # Facebook every 1 hour
    scheduler.add_job(
        run_facebook_cycle,
        trigger=IntervalTrigger(hours=1),
        id="facebook_cycle",
        name="Facebook Posts - Every Hour",
        replace_existing=True,
        misfire_grace_time=300
    )

    # News fetch every 10 minutes
    scheduler.add_job(
        run_news_fetch_only,
        trigger=IntervalTrigger(minutes=10),
        id="news_fetch",
        name="News Fetch - Every 10 Min",
        replace_existing=True,
        misfire_grace_time=60
    )

    logger.info("Scheduler configured!")
    logger.info("Articles: Every 20 min (6AM-10PM)")
    logger.info("Facebook: Every 1 hour (6AM-10PM)")
    logger.info("News: Every 10 min")

    return scheduler


async def start_scheduler():
    """Start the scheduler"""
    from database import init_db
    await init_db()

    scheduler = create_scheduler()
    scheduler.start()

    logger.info("Scheduler started!")
    logger.info("Running first cycle immediately...")

    # Run immediately on start
    await run_article_cycle()
    await asyncio.sleep(10)
    await run_facebook_cycle()

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped!")


if __name__ == "__main__":
    asyncio.run(start_scheduler())
