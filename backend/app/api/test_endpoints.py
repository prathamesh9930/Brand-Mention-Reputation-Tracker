from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import asyncio
from ..services.mention_collector_real import MentionCollector
from ..core.security import verify_api_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test-news-api")
async def test_news_api(api_key_valid: bool = Depends(verify_api_key)):
    """Test News API connection and fetch real data"""
    try:
        # Import the test module
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
        
        from test_news_api import NewsAPITester
        
        tester = NewsAPITester()
        
        # Test API connection
        connection_result = await tester.test_api_connection()
        
        if connection_result['status'] == 'SUCCESS':
            # Test brand search
            search_result = await tester.test_brand_search("Apple")
            
            return {
                "news_api_status": "WORKING",
                "api_key_valid": True,
                "connection_test": connection_result,
                "brand_search_test": search_result,
                "real_data_available": len(search_result.get('articles', [])) > 0,
                "message": "✅ News API is working and fetching real data!"
            }
        else:
            return {
                "news_api_status": "ERROR",
                "api_key_valid": False,
                "error": connection_result.get('error_message', 'Unknown error'),
                "message": "❌ News API is not working. Check your API key."
            }
            
    except Exception as e:
        logger.error(f"Error testing News API: {e}")
        return {
            "news_api_status": "ERROR",
            "error": str(e),
            "message": "❌ Error testing News API connection"
        }

@router.get("/mentions/real-vs-demo")
async def get_real_vs_demo_stats(api_key_valid: bool = Depends(verify_api_key)):
    """Get statistics on real vs demo data in mentions"""
    try:
        from ..models.database import SessionLocal, Mention
        
        db = SessionLocal()
        try:
            # Count mentions by data type
            total_mentions = db.query(Mention).count()
            
            # This would work if we had the is_real_data column
            # real_mentions = db.query(Mention).filter(Mention.is_real_data == True).count()
            # For now, count by source to estimate real vs demo
            
            news_mentions = db.query(Mention).filter(Mention.source == "news").count()
            twitter_mentions = db.query(Mention).filter(Mention.source == "twitter").count()
            reddit_mentions = db.query(Mention).filter(Mention.source == "reddit").count()
            rss_mentions = db.query(Mention).filter(Mention.source == "rss").count()
            
            # Get recent mentions to check for real data indicators
            recent_mentions = db.query(Mention).filter(
                Mention.source == "news"
            ).order_by(Mention.created_at.desc()).limit(5).all()
            
            # Check if any mention URLs contain real domains
            real_data_indicators = 0
            demo_data_indicators = 0
            
            for mention in recent_mentions:
                if mention.source_url and any(domain in mention.source_url for domain in 
                    ['newsapi.org', 'cnn.com', 'bbc.com', 'reuters.com', 'bloomberg.com', 'techcrunch.com']):
                    real_data_indicators += 1
                elif 'demo' in mention.source_url or 'example' in mention.source_url:
                    demo_data_indicators += 1
            
            return {
                "total_mentions": total_mentions,
                "by_source": {
                    "news": news_mentions,
                    "twitter": twitter_mentions,
                    "reddit": reddit_mentions,
                    "rss": rss_mentions
                },
                "data_quality_check": {
                    "recent_news_mentions_checked": len(recent_mentions),
                    "real_data_indicators": real_data_indicators,
                    "demo_data_indicators": demo_data_indicators,
                    "likely_real_data": real_data_indicators > demo_data_indicators
                },
                "message": f"✅ Found {real_data_indicators} mentions with real data indicators out of {len(recent_mentions)} recent news mentions"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting mention statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-real-collection")
async def trigger_real_collection(api_key_valid: bool = Depends(verify_api_key)):
    """Manually trigger real data collection for testing"""
    try:
        from ..models.database import SessionLocal, Brand
        
        # Get a test brand or create one
        db = SessionLocal()
        try:
            test_brand = db.query(Brand).first()
            if not test_brand:
                # Create a test brand
                test_brand = Brand(
                    name="Apple",
                    description="Test brand for real data collection",
                    is_active=True
                )
                db.add(test_brand)
                db.commit()
                db.refresh(test_brand)
                
        finally:
            db.close()
        
        # Use the real mention collector
        collector = MentionCollector()
        
        try:
            # Collect real mentions
            mentions = await collector.collect_news_mentions_real(test_brand)
            
            return {
                "status": "SUCCESS",
                "brand_tested": test_brand.name,
                "mentions_collected": len(mentions),
                "real_data": any(mention.get('is_real_data', False) for mention in mentions),
                "sample_mentions": [
                    {
                        "content": mention["content"][:100] + "...",
                        "source_url": mention["source_url"],
                        "is_real": mention.get("is_real_data", False)
                    }
                    for mention in mentions[:3]
                ],
                "message": f"✅ Successfully collected {len(mentions)} mentions for {test_brand.name}"
            }
            
        finally:
            await collector.close()
            
    except Exception as e:
        logger.error(f"Error triggering real collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))