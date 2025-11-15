import asyncio
import aiohttp
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import re
import os
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class MentionCollector:
    """Service to collect brand mentions from various sources with REAL API integration"""
    
    def __init__(self):
        self.session = None
        # Load real API keys from environment
        self.news_api_key = os.getenv("NEWS_API_KEY", "771f41596a4d4d2ab79a6581c9c01024")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "demo_twitter_token")
        self.use_real_apis = True  # Toggle between real and demo data
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def collect_all_mentions(self) -> List[Dict[str, Any]]:
        """Collect mentions from all active brands and sources"""
        from ..models.database import SessionLocal, Brand
        
        all_mentions = []
        
        # Get active brands
        db = SessionLocal()
        try:
            brands = db.query(Brand).filter(Brand.is_active == True).all()
            
            for brand in brands:
                try:
                    logger.info(f"Collecting mentions for brand: {brand.name}")
                    
                    # Collect from all sources
                    mentions = await asyncio.gather(
                        self.collect_news_mentions_real(brand),  # Real News API
                        self.collect_twitter_mentions(brand),    # Mock for now
                        self.collect_reddit_mentions(brand),     # Mock for now
                        self.collect_rss_mentions(brand),        # Mock for now
                        return_exceptions=True
                    )
                    
                    # Flatten and filter successful results
                    for mention_list in mentions:
                        if isinstance(mention_list, list):
                            all_mentions.extend(mention_list)
                        elif isinstance(mention_list, Exception):
                            logger.error(f"Error collecting mentions: {mention_list}")
                
                except Exception as e:
                    logger.error(f"Error processing brand {brand.name}: {e}")
                    
        finally:
            db.close()
        
        # Store new mentions in database
        if all_mentions:
            await self._store_mentions(all_mentions)
        
        logger.info(f"Collected {len(all_mentions)} new mentions")
        return all_mentions
    
    async def collect_news_mentions_real(self, brand) -> List[Dict[str, Any]]:
        """Collect REAL mentions from News API"""
        try:
            session = await self._get_session()
            mentions = []
            
            # News API endpoint
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": self.news_api_key,
                "q": brand.name,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "en",
                "from": (datetime.now() - timedelta(days=1)).isoformat()  # Last 24 hours
            }
            
            logger.info(f"🔍 Fetching real news data for: {brand.name}")
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    
                    logger.info(f"✅ News API returned {len(articles)} articles for {brand.name}")
                    logger.info(f"📊 Rate limit remaining: {response.headers.get('X-RateLimit-Remaining', 'Unknown')}")
                    
                    for article in articles:
                        # Only include articles that actually mention the brand
                        title = article.get("title", "")
                        description = article.get("description", "")
                        content = f"{title}. {description}"
                        
                        if brand.name.lower() in content.lower():
                            mention = {
                                "brand_id": brand.id,
                                "content": content,
                                "source": "news",
                                "source_url": article.get("url", ""),
                                "author": article.get("author", "Unknown"),
                                "platform_id": f"news_{brand.id}_{hash(article.get('url', ''))}",
                                "created_at": datetime.fromisoformat(
                                    article.get("publishedAt", "").replace("Z", "+00:00")
                                ) if article.get("publishedAt") else datetime.utcnow(),
                                "reach": 1000,  # Default reach for news articles
                                "source_name": article.get("source", {}).get("name", "News Source"),
                                "is_real_data": True  # Flag to identify real vs demo data
                            }
                            mentions.append(mention)
                    
                    logger.info(f"📰 Found {len(mentions)} relevant articles mentioning {brand.name}")
                    
                else:
                    error_data = await response.json()
                    logger.error(f"❌ News API error: {response.status} - {error_data.get('message', 'Unknown error')}")
                    # Fall back to demo data if API fails
                    return await self.collect_news_mentions_demo(brand)
                    
            return mentions
            
        except Exception as e:
            logger.error(f"❌ Error collecting real news mentions for {brand.name}: {e}")
            # Fall back to demo data on error
            return await self.collect_news_mentions_demo(brand)
    
    async def collect_news_mentions_demo(self, brand) -> List[Dict[str, Any]]:
        """Fallback demo news mentions"""
        import random
        mentions = []
        
        sample_articles = [
            f"{brand.name} Reports Strong Q4 Earnings, Stock Rises",
            f"Industry Analysis: How {brand.name} is Changing the Game",
            f"{brand.name} Announces New Partnership with Tech Giant",
            f"Market Watch: {brand.name} Faces New Competition",
            f"Breaking: {brand.name} Launches Revolutionary Product Line",
            f"Expert Opinion: Is {brand.name} Worth the Investment?"
        ]
        
        for i in range(random.randint(0, 2)):
            article_title = random.choice(sample_articles)
            article_content = f"{article_title}. In a recent development, {brand.name} has been making headlines across the industry."
            
            mention = {
                "brand_id": brand.id,
                "content": article_content,
                "source": "news",
                "source_url": f"https://demo-news.com/article/{random.randint(10000, 99999)}",
                "author": f"Demo Journalist {random.randint(1, 100)}",
                "platform_id": f"demo_news_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                "reach": random.randint(1000, 10000),
                "source_name": f"Demo News {random.randint(1, 10)}",
                "is_real_data": False  # Flag for demo data
            }
            mentions.append(mention)
        
        logger.info(f"📰 Generated {len(mentions)} demo articles for {brand.name}")
        return mentions
    
    async def collect_twitter_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from Twitter/X (demo for now - can be upgraded to real API)"""
        try:
            mentions = []
            
            # Generate sample Twitter mentions
            sample_tweets = [
                f"Just tried {brand.name} and I'm absolutely loving it! #amazing",
                f"Not impressed with {brand.name}'s latest update. Could be better.",
                f"{brand.name} customer service is top notch! Highly recommended.",
                f"Why did {brand.name} change their pricing? Not happy about this.",
                f"Been using {brand.name} for years. Still the best in the market!",
                f"{brand.name} just released something interesting. Worth checking out."
            ]
            
            import random
            for i in range(random.randint(0, 3)):
                tweet_text = random.choice(sample_tweets)
                mention = {
                    "brand_id": brand.id,
                    "content": tweet_text,
                    "source": "twitter",
                    "source_url": f"https://twitter.com/user/status/{random.randint(1000000, 9999999)}",
                    "author": f"@user{random.randint(100, 999)}",
                    "platform_id": f"twitter_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
                    "likes": random.randint(0, 100),
                    "shares": random.randint(0, 50),
                    "comments": random.randint(0, 25),
                    "is_real_data": False
                }
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error collecting Twitter mentions for {brand.name}: {e}")
            return []
    
    async def collect_reddit_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from Reddit (demo for now)"""
        # Same as before but with is_real_data: False flag
        try:
            mentions = []
            sample_posts = [
                f"Has anyone tried {brand.name}? Looking for honest reviews.",
                f"Just switched to {brand.name} and the difference is night and day!",
                f"PSA: {brand.name} is having some issues today. Anyone else experiencing this?",
                f"Why I think {brand.name} is overrated (unpopular opinion)",
                f"Been using {brand.name} for 6 months - here's my detailed review",
                f"{brand.name} vs competitors - comprehensive comparison"
            ]
            
            import random
            for i in range(random.randint(0, 2)):
                post_content = random.choice(sample_posts)
                mention = {
                    "brand_id": brand.id,
                    "content": post_content,
                    "source": "reddit",
                    "source_url": f"https://reddit.com/r/reviews/comments/{random.randint(100000, 999999)}",
                    "author": f"u/redditor{random.randint(100, 999)}",
                    "platform_id": f"reddit_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                    "likes": random.randint(1, 500),
                    "comments": random.randint(5, 100),
                    "is_real_data": False
                }
                mentions.append(mention)
            
            return mentions
        except Exception as e:
            logger.error(f"Error collecting Reddit mentions for {brand.name}: {e}")
            return []
    
    async def collect_rss_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from RSS feeds (demo for now)"""
        # Same as before but with is_real_data: False flag
        try:
            mentions = []
            sample_blogs = [
                f"My Experience with {brand.name}: A Detailed Review",
                f"10 Things You Didn't Know About {brand.name}",
                f"How {brand.name} Helped Me Solve My Business Problem",
                f"The Rise of {brand.name}: A Success Story",
                f"Comparing {brand.name} to Its Main Competitors",
                f"{brand.name} Tutorial: Getting Started Guide"
            ]
            
            import random
            for i in range(random.randint(0, 1)):
                blog_title = random.choice(sample_blogs)
                blog_content = f"{blog_title}. This comprehensive blog post explores various aspects of {brand.name}."
                
                mention = {
                    "brand_id": brand.id,
                    "content": blog_content,
                    "source": "rss",
                    "source_url": f"https://tech-blog-{random.randint(1, 100)}.com/posts/{random.randint(1000, 9999)}",
                    "author": f"Blogger{random.randint(1, 50)}",
                    "platform_id": f"rss_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                    "is_real_data": False
                }
                mentions.append(mention)
            
            return mentions
        except Exception as e:
            logger.error(f"Error collecting RSS mentions for {brand.name}: {e}")
            return []
    
    async def _store_mentions(self, mentions: List[Dict[str, Any]]):
        """Store new mentions in the database"""
        from ..models.database import SessionLocal, Mention
        
        db = SessionLocal()
        try:
            stored_count = 0
            real_data_count = 0
            
            for mention_data in mentions:
                # Check if mention already exists
                existing = db.query(Mention).filter(
                    Mention.platform_id == mention_data["platform_id"]
                ).first()
                
                if not existing:
                    mention = Mention(**mention_data)
                    db.add(mention)
                    stored_count += 1
                    
                    if mention_data.get("is_real_data", False):
                        real_data_count += 1
            
            db.commit()
            logger.info(f"📊 Stored {stored_count} new mentions ({real_data_count} from real APIs, {stored_count - real_data_count} demo)")
            
        except Exception as e:
            logger.error(f"Error storing mentions: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()