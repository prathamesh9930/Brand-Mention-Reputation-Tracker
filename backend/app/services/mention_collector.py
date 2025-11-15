import asyncio
import aiohttp
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class MentionCollector:
    """Service to collect brand mentions from various sources"""
    
    def __init__(self):
        self.session = None
        # Mock API keys for demo - in production, use environment variables
        self.news_api_key = "demo_news_api_key"
        self.twitter_bearer_token = "demo_twitter_token"
        
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
                        self.collect_twitter_mentions(brand),
                        self.collect_reddit_mentions(brand),
                        self.collect_news_mentions(brand),
                        self.collect_rss_mentions(brand),
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
    
    async def collect_twitter_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from Twitter/X (enhanced simulated content)"""
        try:
            mentions = []
            
            import random
            
            # Enhanced variety of tweet templates
            positive_tweets = [
                f"Just tried {brand.name} and I'm absolutely loving it! #amazing",
                f"{brand.name} customer service is top notch! Highly recommended.",
                f"Been using {brand.name} for years. Still the best in the market!",
                f"{brand.name} just released something interesting. Worth checking out.",
                f"Wow! {brand.name} exceeded my expectations today 🔥",
                f"Can't believe how good {brand.name} is! Game changer 💯",
                f"Shoutout to {brand.name} for making my day better ✨",
                f"{brand.name} is doing things right. Impressed! 👏",
                f"Finally found something that works - thank you {brand.name}!",
                f"{brand.name} team deserves recognition for this quality 🙌"
            ]
            
            negative_tweets = [
                f"Not impressed with {brand.name}'s latest update. Could be better.",
                f"Why did {brand.name} change their pricing? Not happy about this.",
                f"{brand.name} disappointed me today. Expected more 😞",
                f"Having issues with {brand.name} again... when will this be fixed?",
                f"{brand.name} support took forever to respond. Frustrated!",
                f"Used to love {brand.name} but quality has declined lately",
                f"{brand.name} needs to step up their game. Competition is better.",
                f"Considering switching from {brand.name}. Too many problems."
            ]
            
            neutral_tweets = [
                f"Anyone else using {brand.name}? What's your experience?",
                f"Thinking about trying {brand.name}. Any reviews?",
                f"{brand.name} announced new features today. Checking it out.",
                f"Comparing {brand.name} with alternatives. Still deciding.",
                f"Tutorial: How to get started with {brand.name} - thread 🧵",
                f"{brand.name} is trending today. What's the buzz about?",
                f"Quick question: Is {brand.name} worth the investment?",
                f"Breaking: {brand.name} releases quarterly update"
            ]
            
            # Combine all tweet types
            all_tweets = positive_tweets + negative_tweets + neutral_tweets
            
            # Add time-based variety
            time_variants = [
                "this morning", "yesterday", "last week", "recently", "today", 
                "right now", "just now", "a few minutes ago", "this afternoon"
            ]
            
            # Generate more dynamic content with realistic engagement
            for i in range(random.randint(0, 4)):  # 0-4 mentions per cycle
                base_tweet = random.choice(all_tweets)
                
                # Determine sentiment for realistic engagement
                if any(word in base_tweet.lower() for word in ['love', 'amazing', 'best', 'great', 'excellent', 'wow', 'impressed']):
                    sentiment_type = 'positive'
                elif any(word in base_tweet.lower() for word in ['not impressed', 'disappointed', 'frustrated', 'problems', 'issues']):
                    sentiment_type = 'negative'
                else:
                    sentiment_type = 'neutral'
                
                # Add occasional time context
                if random.random() < 0.3:  # 30% chance to add time context
                    time_context = random.choice(time_variants)
                    enhanced_tweet = f"{base_tweet} (tried it {time_context})"
                else:
                    enhanced_tweet = base_tweet
                
                # Add occasional emojis or hashtags
                if random.random() < 0.4:  # 40% chance
                    emojis = ["🚀", "💪", "👍", "⭐", "🔥", "💯", "✨", "🎯", "🌟", "👏"]
                    enhanced_tweet += f" {random.choice(emojis)}"
                
                # **REALISTIC ENGAGEMENT BASED ON CONTENT**
                if sentiment_type == 'positive':
                    # Positive content gets more engagement
                    likes = random.randint(15, 250)
                    shares = random.randint(3, max(1, likes // 4))  # Shares are typically 1/4 of likes
                    comments = random.randint(2, max(1, likes // 8))  # Comments are fewer
                elif sentiment_type == 'negative':
                    # Negative content gets moderate engagement (people engage with controversy)
                    likes = random.randint(8, 120)
                    shares = random.randint(1, max(1, likes // 6))
                    comments = random.randint(5, max(1, likes // 3))  # More comments on negative posts
                else:
                    # Neutral content gets lower engagement
                    likes = random.randint(2, 80)
                    shares = random.randint(0, max(1, likes // 8)) if likes > 8 else random.randint(0, 2)
                    comments = random.randint(1, max(1, likes // 6)) if likes > 6 else random.randint(0, 2)
                
                # Ensure logical relationships (shares <= likes, comments <= likes)
                shares = min(shares, likes)
                comments = min(comments, likes)
                
                mention = {
                    "brand_id": brand.id,
                    "content": enhanced_tweet,
                    "source": "twitter",
                    "source_url": f"https://twitter.com/user/status/{random.randint(1000000, 9999999)}",
                    "author": f"@user{random.randint(100, 999)}",
                    "platform_id": f"twitter_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(minutes=random.randint(1, 120)),
                    "likes": likes,
                    "shares": shares,
                    "comments": comments
                }
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error collecting Twitter mentions for {brand.name}: {e}")
            return []
    
    async def collect_reddit_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from Reddit (enhanced simulated content)"""
        try:
            mentions = []
            import random
            
            # Diverse Reddit post types
            review_posts = [
                f"Has anyone tried {brand.name}? Looking for honest reviews.",
                f"Just switched to {brand.name} and the difference is night and day!",
                f"Been using {brand.name} for 6 months - here's my detailed review",
                f"Why I think {brand.name} is overrated (unpopular opinion)",
                f"{brand.name} vs competitors - comprehensive comparison",
                f"My 1-year experience with {brand.name} - AMA"
            ]
            
            discussion_posts = [
                f"PSA: {brand.name} is having some issues today. Anyone else experiencing this?",
                f"Discussion: What do you think about {brand.name}'s latest move?",
                f"Is {brand.name} worth it in 2025? Let's discuss.",
                f"How has {brand.name} changed your workflow/life?",
                f"Unpopular opinion: {brand.name} is actually underrated",
                f"Weekly {brand.name} discussion thread - share your thoughts"
            ]
            
            help_posts = [
                f"Need help choosing between {brand.name} and alternatives",
                f"New to {brand.name} - any tips for beginners?",
                f"Best practices for using {brand.name} effectively?",
                f"Troubleshooting {brand.name} - common solutions",
                f"How to maximize value from {brand.name}?",
                f"Complete guide to {brand.name} for newcomers"
            ]
            
            news_posts = [
                f"Breaking: {brand.name} announces major update",
                f"Industry news: {brand.name} partners with major company",
                f"{brand.name} stock hits new high after latest announcement",
                f"Leaked: {brand.name} working on revolutionary feature",
                f"Analysis: How {brand.name} is disrupting the industry",
                f"Market update: {brand.name} reports record growth"
            ]
            
            all_posts = review_posts + discussion_posts + help_posts + news_posts
            
            for i in range(random.randint(0, 3)):  # 0-3 posts per cycle
                post_content = random.choice(all_posts)
                
                # Add occasional context
                if random.random() < 0.3:
                    contexts = ["Update:", "Follow-up:", "EDIT:", "TL;DR:", "Update after 24h:"]
                    post_content = f"{random.choice(contexts)} {post_content}"
                
                subreddits = ["technology", "reviews", "business", "startups", "ProductHunt", 
                             "entrepreneur", "investing", "gadgets", "software", "apps"]
                subreddit = random.choice(subreddits)
                
                # **REALISTIC REDDIT ENGAGEMENT BASED ON CONTENT SENTIMENT**
                if any(word in post_content.lower() for word in ['love', 'amazing', 'great', 'excellent', 'recommend', 'perfect']):
                    # Positive posts get more upvotes, fewer comments
                    upvotes = random.randint(25, 500)
                    comments = random.randint(3, min(50, upvotes // 8))
                elif any(word in post_content.lower() for word in ['disappointed', 'terrible', 'avoid', 'worst', 'awful', 'frustrating']):
                    # Negative posts get controversial voting and more discussion
                    upvotes = random.randint(5, 200)
                    comments = random.randint(8, min(80, upvotes // 3))
                else:
                    # Neutral posts get moderate engagement  
                    upvotes = random.randint(10, 150)
                    comments = random.randint(2, min(30, upvotes // 6))
                
                # Occasional viral post (10% chance)
                if random.random() < 0.1:
                    upvotes *= random.randint(2, 4)
                    comments = min(200, comments * 2)
                
                mention = {
                    "brand_id": brand.id,
                    "content": post_content,
                    "source": "reddit",
                    "source_url": f"https://reddit.com/r/{subreddit}/comments/{random.randint(100000, 999999)}",
                    "author": f"u/{random.choice(['tech_guru', 'daily_user', 'startup_watcher', 'honest_reviewer', 'consumer_voice'])}",
                    "platform_id": f"reddit_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                    "likes": upvotes,  # Reddit upvotes  
                    "shares": 0,  # Reddit doesn't have shares
                    "comments": comments
                }
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error collecting Reddit mentions for {brand.name}: {e}")
            return []
    
    async def collect_news_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from news sources (simulated for demo)"""
        try:
            mentions = []
            
            # Generate sample news articles
            sample_articles = [
                f"{brand.name} Reports Strong Q4 Earnings, Stock Rises",
                f"Industry Analysis: How {brand.name} is Changing the Game",
                f"{brand.name} Announces New Partnership with Tech Giant",
                f"Market Watch: {brand.name} Faces New Competition",
                f"Breaking: {brand.name} Launches Revolutionary Product Line",
                f"Expert Opinion: Is {brand.name} Worth the Investment?"
            ]
            
            import random
            for i in range(random.randint(0, 2)):
                article_title = random.choice(sample_articles)
                article_content = f"{article_title}. In a recent development, {brand.name} has been making headlines across the industry. Analysts are closely watching the company's performance and market response."
                
                mention = {
                    "brand_id": brand.id,
                    "content": article_content,
                    "source": "news",
                    "source_url": f"https://example-news.com/article/{random.randint(10000, 99999)}",
                    "author": f"Journalist {random.randint(1, 100)}",
                    "platform_id": f"news_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                    "reach": random.randint(1000, 10000)
                }
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error collecting news mentions for {brand.name}: {e}")
            return []
    
    async def collect_rss_mentions(self, brand) -> List[Dict[str, Any]]:
        """Collect mentions from RSS feeds (simulated for demo)"""
        try:
            mentions = []
            
            # Generate sample blog posts
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
                blog_content = f"{blog_title}. This comprehensive blog post explores various aspects of {brand.name} and provides insights based on real user experience."
                
                mention = {
                    "brand_id": brand.id,
                    "content": blog_content,
                    "source": "rss",
                    "source_url": f"https://tech-blog-{random.randint(1, 100)}.com/posts/{random.randint(1000, 9999)}",
                    "author": f"Blogger{random.randint(1, 50)}",
                    "platform_id": f"rss_{brand.id}_{datetime.utcnow().timestamp()}_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
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
            for mention_data in mentions:
                # Check if mention already exists
                existing = db.query(Mention).filter(
                    Mention.platform_id == mention_data["platform_id"]
                ).first()
                
                if not existing:
                    mention = Mention(**mention_data)
                    db.add(mention)
                    stored_count += 1
            
            db.commit()
            logger.info(f"Stored {stored_count} new mentions in database")
            
        except Exception as e:
            logger.error(f"Error storing mentions: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()