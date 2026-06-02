from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship("Article", back_populates="category")
    raw_news = relationship("RawNews", back_populates="category")


class RawNews(Base):
    __tablename__ = "raw_news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(200), nullable=True)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    category = relationship("Category", back_populates="raw_news")


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    meta_description = Column(String(300), nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    featured_image = Column(String(1000), nullable=True)
    og_image = Column(String(1000), nullable=True)
    faq = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    hashtags = Column(String(500), nullable=True)
    language = Column(String(10), default="hi")
    ai_provider = Column(String(50), nullable=True)
    word_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    is_facebook_posted = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    raw_news_id = Column(Integer, ForeignKey("raw_news.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    category = relationship("Category", back_populates="articles")
    affiliate_products = relationship("AffiliateProduct", back_populates="article")
    facebook_posts = relationship("FacebookPost", back_populates="article")


class AffiliateProduct(Base):
    __tablename__ = "affiliate_products"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    product_name = Column(String(500), nullable=False)
    product_url = Column(String(1000), nullable=False)
    product_image = Column(String(1000), nullable=True)
    price = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    article = relationship("Article", back_populates="affiliate_products")


class FacebookPost(Base):
    __tablename__ = "facebook_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    post_type = Column(String(50), default="article")
    content = Column(Text, nullable=False)
    image_url = Column(String(1000), nullable=True)
    hashtags = Column(String(500), nullable=True)
    fb_post_id = Column(String(200), nullable=True)
    is_posted = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    article = relationship("Article", back_populates="facebook_posts")


class AIUsage(Base):
    __tablename__ = "ai_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, default=0)
    task_type = Column(String(100), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    response_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
