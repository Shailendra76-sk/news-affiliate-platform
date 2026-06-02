import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from news_fetcher import fetch_all_news
from article_generator import generate_articles_batch
from image_manager import attach_images_to_articles
from affiliate_engine import attach_affiliate_to_articles
from facebook_manager import run_facebook_automation
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# How many articles per cycle
ARTICLES_PER_CYCLE = int(os.getenv("ARTICLES_PER_CYCLE", "5"))

# Fetch interval in hours
FETCH_INTERVAL = int(os.getenv("NEWS_FETCH_INTERVAL", "2"))


async def run_full_cycle():
    """
    Full automation cycle:
    1. Fetch news
    2. Generate articles
    3. Attach images
    4. Attach affiliate products
    5. Post to Facebook
    """
    start_time = datetime.utcnow()
    logger.info("=" * 50)
    logger.info(f"Automation cycle started: {start_time}")
    logger.info("=" * 50)

    try:
        # Step 1: Fetch News
        logger.info("Step 1: Fetching news...")
        news_count = await fetch_all_news()
        logger.info(f"News fetched: {news_count}")

        # Wait a bit
        await asyncio.sleep(5)

        # Step 2: Generate Articles
        logger.info("Step 2: Generating articles...")
        article_count = await generate_articles_batch(
            count=ARTICLES_PER_CYCLE
        )
        logger.info(f"Articles generated: {article_count}")

        # Wait a bit
        await asyncio.sleep(5)

        # Step 3: Attach Images
        logger.info("Step 3: Attaching images...")
        await attach_images_to_articles()
        logger.info("Images attached!")

        # Wait a bit
        await asyncio.sleep(3)

        # Step 4: Attach Affiliate Products
        logger.info("Step 4: Attaching affiliate products...")
        await attach_affiliate_to_articles()
        logger.info("Affiliate products attached!")

        # Wait a bit
        await asyncio.sleep(3)

        # Step 5: Facebook Automation
        logger.info("Step 5: Running Facebook automation...")
        await run_facebook_automation()
        logger.info("Facebook posts done!")

        end_time = datetime.utcnow()
        duration = (end_time - start_time).seconds

        logger.info("=" * 50)
        logger.info(f"Cycle complete! Duration: {duration}s")
        logger.info(f"News: {news_count}, Articles: {article_count}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error in automation cycle: {e}")


async def run_news_only():
    """Only fetch news - runs more frequently"""
    logger.info("Running news-only fetch...")
    try:
        count = await fetch_all_news()
        logger.info(f"News fetched: {count}")
    except Exception as e:
        logger.error(f"News fetch error: {e}")


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler"""
    scheduler = AsyncIOScheduler()

    # Full cycle every 2 hours
    scheduler.add_job(
        run_full_cycle,
        trigger=IntervalTrigger(hours=FETCH_INTERVAL),
        id="full_cycle",
        name="Full Automation Cycle",
        replace_existing=True,
        misfire_grace_time=300
    )

    # News only every 30 minutes
    scheduler.add_job(
        run_news_only,
        trigger=IntervalTrigger(minutes=30),
        id="news_fetch",
        name="News Fetch Only",
        replace_existing=True,
        misfire_grace_time=60
    )

    logger.info(
        f"Scheduler configured! "
        f"Full cycle every {FETCH_INTERVAL}h, "
        f"News every 30min"
    )

    return scheduler


async def start_scheduler():
    """Start the scheduler"""
    from database import init_db
    await init_db()

    scheduler = create_scheduler()
    scheduler.start()

    logger.info("Scheduler started!")
    logger.info("Running first cycle immediately...")

    # Run first cycle immediately
    await run_full_cycle()

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped!")


if __name__ == "__main__":
    asyncio.run(start_scheduler())
