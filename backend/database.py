from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from models import Base, Category
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./news_platform.db")

# Fix URL for async
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Insert default categories
    async with AsyncSessionLocal() as session:
        try:
            from sqlalchemy import select
            result = await session.execute(select(Category))
            existing = result.scalars().all()
            
            if not existing:
                categories = [
                    Category(name="Technology", slug="technology", 
                            description="Tech news", icon="💻"),
                    Category(name="Sports", slug="sports", 
                            description="Sports news", icon="🏏"),
                    Category(name="Business", slug="business", 
                            description="Business news", icon="💼"),
                    Category(name="Entertainment", slug="entertainment", 
                            description="Entertainment news", icon="🎬"),
                    Category(name="Education", slug="education", 
                            description="Education news", icon="📚"),
                    Category(name="World", slug="world", 
                            description="World news", icon="🌍"),
                    Category(name="India", slug="india", 
                            description="India news", icon="🇮🇳"),
                    Category(name="General", slug="general", 
                            description="General news", icon="📰"),
                ]
                
                for category in categories:
                    session.add(category)
                
                await session.commit()
                logger.info("Default categories created!")
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating categories: {e}")
