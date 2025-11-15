import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NewsAPITester:
    """Test real News API integration"""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY", "771f41596a4d4d2ab79a6581c9c01024")
        self.base_url = "https://newsapi.org/v2"
        
    async def test_api_connection(self) -> Dict[str, Any]:
        """Test if News API is working with your key"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                params = {
                    "apiKey": self.news_api_key,
                    "country": "us",
                    "pageSize": 5
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "SUCCESS",
                            "api_key_valid": True,
                            "total_results": data.get("totalResults", 0),
                            "articles_returned": len(data.get("articles", [])),
                            "sample_headline": data.get("articles", [{}])[0].get("title", "No articles") if data.get("articles") else "No articles",
                            "api_response_time": response.headers.get("response-time", "unknown"),
                            "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining", "unknown")
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "status": "ERROR",
                            "api_key_valid": False,
                            "error_code": response.status,
                            "error_message": error_data.get("message", "Unknown error"),
                            "error_details": error_data
                        }
                        
        except Exception as e:
            return {
                "status": "ERROR",
                "api_key_valid": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def test_brand_search(self, brand_name: str) -> Dict[str, Any]:
        """Test searching for mentions of a specific brand"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                params = {
                    "apiKey": self.news_api_key,
                    "q": brand_name,
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "language": "en"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("articles", [])
                        
                        return {
                            "status": "SUCCESS",
                            "brand_searched": brand_name,
                            "total_results": data.get("totalResults", 0),
                            "articles_returned": len(articles),
                            "articles": [
                                {
                                    "title": article.get("title", ""),
                                    "description": article.get("description", ""),
                                    "source": article.get("source", {}).get("name", ""),
                                    "published_at": article.get("publishedAt", ""),
                                    "url": article.get("url", "")
                                }
                                for article in articles[:3]  # First 3 articles
                            ],
                            "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining", "unknown")
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "status": "ERROR",
                            "error_code": response.status,
                            "error_message": error_data.get("message", "Unknown error")
                        }
                        
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "error_type": type(e).__name__
            }

# Test function you can run directly
async def run_tests():
    """Run all News API tests"""
    print("🔍 Testing News API Integration...")
    print("=" * 50)
    
    tester = NewsAPITester()
    
    # Test 1: API Connection
    print("📡 Test 1: API Connection Test")
    connection_result = await tester.test_api_connection()
    print(f"Status: {connection_result['status']}")
    print(f"API Key Valid: {connection_result.get('api_key_valid', False)}")
    
    if connection_result['status'] == 'SUCCESS':
        print(f"✅ Total Results Available: {connection_result.get('total_results', 0)}")
        print(f"✅ Articles Returned: {connection_result.get('articles_returned', 0)}")
        print(f"✅ Sample Headline: {connection_result.get('sample_headline', 'None')}")
        print(f"✅ Rate Limit Remaining: {connection_result.get('rate_limit_remaining', 'Unknown')}")
    else:
        print(f"❌ Error: {connection_result.get('error_message', 'Unknown error')}")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Brand Search
    test_brands = ["Apple", "Microsoft", "Tesla", "Google", "Amazon"]
    
    for brand in test_brands:
        print(f"🔍 Test 2: Searching for '{brand}' mentions...")
        search_result = await tester.test_brand_search(brand)
        
        if search_result['status'] == 'SUCCESS':
            print(f"✅ Found {search_result.get('total_results', 0)} articles mentioning '{brand}'")
            print(f"✅ Returned {search_result.get('articles_returned', 0)} articles")
            
            if search_result.get('articles'):
                print("📰 Sample Articles:")
                for i, article in enumerate(search_result['articles'], 1):
                    print(f"   {i}. {article['title']}")
                    print(f"      Source: {article['source']}")
                    print(f"      Published: {article['published_at']}")
            
            print(f"✅ Rate Limit Remaining: {search_result.get('rate_limit_remaining', 'Unknown')}")
            break  # Test with just one brand for now
        else:
            print(f"❌ Error searching for {brand}: {search_result.get('error_message', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("🎯 News API Test Complete!")

if __name__ == "__main__":
    asyncio.run(run_tests())