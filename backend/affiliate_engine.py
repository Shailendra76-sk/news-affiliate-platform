import os
import logging
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from sqlalchemy import select
from models import Article, AffiliateProduct, Category
from database import AsyncSessionLocal
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IN")

# ========================================
# CATEGORY TO PRODUCT MAPPING
# ========================================

CATEGORY_PRODUCTS = {
    "technology": [
        {
            "name": "Smartphones",
            "keywords": "smartphone mobile phone",
            "search_term": "best smartphones india 2024",
            "default_products": [
                {
                    "name": "Samsung Galaxy S24 Ultra",
                    "search": "Samsung+Galaxy+S24",
                    "price": "₹1,29,999",
                    "image": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=300"
                },
                {
                    "name": "Apple iPhone 15",
                    "search": "Apple+iPhone+15",
                    "price": "₹79,999",
                    "image": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300"
                },
                {
                    "name": "OnePlus 12",
                    "search": "OnePlus+12",
                    "price": "₹64,999",
                    "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300"
                }
            ]
        },
        {
            "name": "Laptops",
            "keywords": "laptop computer",
            "search_term": "best laptops india 2024",
            "default_products": [
                {
                    "name": "Apple MacBook Air M2",
                    "search": "Apple+MacBook+Air+M2",
                    "price": "₹1,14,999",
                    "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300"
                },
                {
                    "name": "Dell XPS 15",
                    "search": "Dell+XPS+15",
                    "price": "₹1,89,999",
                    "image": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=300"
                },
                {
                    "name": "HP Pavilion Gaming",
                    "search": "HP+Pavilion+Gaming+Laptop",
                    "price": "₹74,999",
                    "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=300"
                }
            ]
        },
        {
            "name": "Earbuds & Headphones",
            "keywords": "earbuds headphones audio",
            "search_term": "best earbuds india 2024",
            "default_products": [
                {
                    "name": "Sony WH-1000XM5",
                    "search": "Sony+WH-1000XM5",
                    "price": "₹29,999",
                    "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300"
                },
                {
                    "name": "Apple AirPods Pro",
                    "search": "Apple+AirPods+Pro",
                    "price": "₹24,999",
                    "image": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=300"
                },
                {
                    "name": "boAt Rockerz 550",
                    "search": "boAt+Rockerz+550",
                    "price": "₹1,999",
                    "image": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300"
                }
            ]
        }
    ],
    "sports": [
        {
            "name": "Cricket Equipment",
            "keywords": "cricket bat ball",
            "search_term": "cricket equipment india",
            "default_products": [
                {
                    "name": "SS Ton Cricket Bat",
                    "search": "SS+Ton+Cricket+Bat",
                    "price": "₹3,999",
                    "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=300"
                },
                {
                    "name": "SG Cricket Kit",
                    "search": "SG+Cricket+Kit+Bag",
                    "price": "₹8,999",
                    "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=300"
                },
                {
                    "name": "Nivia Cricket Ball",
                    "search": "Nivia+Cricket+Ball",
                    "price": "₹499",
                    "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=300"
                }
            ]
        },
        {
            "name": "Sports Gear",
            "keywords": "sports fitness gym",
            "search_term": "sports fitness equipment india",
            "default_products": [
                {
                    "name": "Cosco Fitness Kit",
                    "search": "Cosco+Fitness+Kit",
                    "price": "₹2,499",
                    "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300"
                },
                {
                    "name": "Adidas Running Shoes",
                    "search": "Adidas+Running+Shoes+India",
                    "price": "₹5,999",
                    "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300"
                },
                {
                    "name": "Nike Sports Jersey",
                    "search": "Nike+Sports+Jersey+India",
                    "price": "₹2,999",
                    "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=300"
                }
            ]
        }
    ],
    "education": [
        {
            "name": "Books & Study Material",
            "keywords": "books study material",
            "search_term": "best books india education",
            "default_products": [
                {
                    "name": "UPSC Preparation Books Set",
                    "search": "UPSC+Preparation+Books+Set",
                    "price": "₹2,999",
                    "image": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300"
                },
                {
                    "name": "Class 12 NCERT Books Set",
                    "search": "NCERT+Books+Class+12+Set",
                    "price": "₹1,499",
                    "image": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300"
                },
                {
                    "name": "Kindle Paperwhite",
                    "search": "Kindle+Paperwhite+India",
                    "price": "₹13,999",
                    "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300"
                }
            ]
        }
    ],
    "business": [
        {
            "name": "Business Tools",
            "keywords": "business office productivity",
            "search_term": "business productivity tools india",
            "default_products": [
                {
                    "name": "HP LaserJet Printer",
                    "search": "HP+LaserJet+Printer+India",
                    "price": "₹14,999",
                    "image": "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=300"
                },
                {
                    "name": "Logitech MX Master Mouse",
                    "search": "Logitech+MX+Master+Mouse",
                    "price": "₹8,995",
                    "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300"
                },
                {
                    "name": "Mechanical Keyboard",
                    "search": "Mechanical+Keyboard+India",
                    "price": "₹3,999",
                    "image": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=300"
                }
            ]
        }
    ],
    "entertainment": [
        {
            "name": "Entertainment Gadgets",
            "keywords": "entertainment tv streaming",
            "search_term": "entertainment gadgets india",
            "default_products": [
                {
                    "name": "Amazon Fire TV Stick 4K",
                    "search": "Amazon+Fire+TV+Stick+4K",
                    "price": "₹6,999",
                    "image": "https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?w=300"
                },
                {
                    "name": "JBL Party Box Speaker",
                    "search": "JBL+Party+Box+Speaker",
                    "price": "₹19,999",
                    "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=300"
                },
                {
                    "name": "GoPro Hero 12",
                    "search": "GoPro+Hero+12",
                    "price": "₹39,999",
                    "image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300"
                }
            ]
        }
    ],
    "general": [
        {
            "name": "Popular Products",
            "keywords": "popular bestseller india",
            "search_term": "bestseller products india",
            "default_products": [
                {
                    "name": "Echo Dot 5th Gen",
                    "search": "Echo+Dot+5th+Gen",
                    "price": "₹4,999",
                    "image": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=300"
                },
                {
                    "name": "Instant Pot Duo",
                    "search": "Instant+Pot+Duo+India",
                    "price": "₹8,999",
                    "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=300"
                },
                {
                    "name": "Philips Air Fryer",
                    "search": "Philips+Air+Fryer+India",
                    "price": "₹7,995",
                    "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=300"
                }
            ]
        }
    ]
}


def generate_amazon_affiliate_url(search_term: str) -> str:
    """Generate Amazon affiliate search URL"""
    associate_tag = AMAZON_ASSOCIATE_TAG or "yourtag-21"
    
    base_url = "https://www.amazon.in/s"
    params = {
        "k": search_term,
        "tag": associate_tag,
        "ref": "nb_sb_noss"
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


def generate_product_affiliate_url(search: str) -> str:
    """Generate direct product affiliate URL"""
    associate_tag = AMAZON_ASSOCIATE_TAG or "yourtag-21"
    
    base_url = "https://www.amazon.in/s"
    params = {
        "k": search.replace("+", " "),
        "tag": associate_tag
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


async def get_products_for_category(category_slug: str) -> list:
    """Get relevant products for a category"""
    
    category_data = CATEGORY_PRODUCTS.get(
        category_slug,
        CATEGORY_PRODUCTS["general"]
    )
    
    products = []
    
    for product_group in category_data:
        for product in product_group["default_products"]:
            affiliate_url = generate_product_affiliate_url(
                product["search"]
            )
            
            products.append({
                "name": product["name"],
                "price": product["price"],
                "image": product["image"],
                "affiliate_url": affiliate_url,
                "category": product_group["name"]
            })
    
    return products[:6]


async def save_affiliate_products(article_id: int, category_slug: str):
    """Save affiliate products for an article"""
    
    products = await get_products_for_category(category_slug)
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if products already exist
            existing = await session.execute(
                select(AffiliateProduct).where(
                    AffiliateProduct.article_id == article_id
                )
            )
            if existing.scalars().all():
                logger.info(
                    f"Affiliate products already exist for article {article_id}"
                )
                return
            
            for product in products:
                affiliate_product = AffiliateProduct(
                    article_id=article_id,
                    product_name=product["name"],
                    product_url=product["affiliate_url"],
                    product_image=product["image"],
                    price=product["price"],
                    category=product["category"]
                )
                session.add(affiliate_product)
            
            await session.commit()
            logger.info(
                f"Saved {len(products)} affiliate products "
                f"for article {article_id}"
            )
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving affiliate products: {e}")


async def attach_affiliate_to_articles():
    """Attach affiliate products to articles that don't have them"""
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Article).where(
                    Article.is_published == True
                ).limit(20)
            )
            articles = result.scalars().all()
            
            for article in articles:
                # Check if already has products
                products_result = await session.execute(
                    select(AffiliateProduct).where(
                        AffiliateProduct.article_id == article.id
                    )
                )
                existing_products = products_result.scalars().all()
                
                if not existing_products:
                    category_slug = "general"
                    
                    if article.category_id:
                        cat_result = await session.execute(
                            select(Category).where(
                                Category.id == article.category_id
                            )
                        )
                        category = cat_result.scalar_one_or_none()
                        if category:
                            category_slug = category.slug
                    
                    await save_affiliate_products(
                        article.id, 
                        category_slug
                    )
            
            logger.info("Affiliate products attachment complete!")
            
        except Exception as e:
            logger.error(f"Error in affiliate attachment: {e}")


async def track_affiliate_click(product_id: int):
    """Track affiliate product click"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(AffiliateProduct).where(
                    AffiliateProduct.id == product_id
                )
            )
            product = result.scalar_one_or_none()
            
            if product:
                product.clicks += 1
                await session.commit()
                return product.product_url
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Error tracking click: {e}")
            return None
