"""
Simple sentiment analyzer without scikit-learn dependencies for demo purposes
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Simple rule-based sentiment analysis service"""
    
    def __init__(self):
        self.model_loaded = True
        # Simple sentiment word lists
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'like', 'fantastic', 
            'wonderful', 'perfect', 'best', 'outstanding', 'superb', 'brilliant', 'incredible',
            'happy', 'satisfied', 'pleased', 'delighted', 'impressed', 'recommend', 'quality',
            'fast', 'reliable', 'helpful', 'friendly', 'professional', 'efficient', 'smooth'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'worst', 'disappointing',
            'poor', 'disgusting', 'useless', 'broken', 'slow', 'expensive', 'cheap', 'fake',
            'angry', 'frustrated', 'annoyed', 'upset', 'disappointed', 'complain', 'problem',
            'issue', 'bug', 'error', 'fail', 'crashed', 'stuck', 'frozen', 'lag', 'glitch'
        }
    
    async def process_pending_mentions(self) -> List[Dict[str, Any]]:
        """Process mentions that need sentiment analysis"""
        from ..models.database import SessionLocal, Mention
        
        db = SessionLocal()
        processed_mentions = []
        
        try:
            # Get mentions without sentiment analysis
            mentions = db.query(Mention).filter(
                Mention.sentiment_label == None
            ).limit(50).all()
            
            for mention in mentions:
                try:
                    # Analyze sentiment - ensure we get the actual string content
                    content_text = str(mention.content)  # type: ignore
                    sentiment_result = await self.analyze_sentiment(content_text)
                    
                    # Update mention with results
                    mention.sentiment_score = sentiment_result['score']
                    mention.sentiment_label = sentiment_result['label']
                    mention.confidence = sentiment_result['confidence']
                    
                    processed_mentions.append({
                        'id': mention.id,
                        'brand_id': mention.brand_id,
                        'sentiment_score': mention.sentiment_score,
                        'sentiment_label': mention.sentiment_label,
                        'confidence': mention.confidence,
                        'content': str(mention.content)[:100] + '...' if len(str(mention.content)) > 100 else str(mention.content)  # type: ignore
                    })
                    
                    logger.info(f"Processed sentiment for mention {mention.id}: {sentiment_result['label']} ({sentiment_result['score']:.3f})")
                    
                except Exception as e:
                    logger.error(f"Error processing mention {mention.id}: {str(e)}")
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in sentiment processing: {str(e)}")
        finally:
            db.close()
        
        return processed_mentions
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        try:
            cleaned_text = self._clean_text(text)
            result = self._rule_based_sentiment(cleaned_text)
            
            logger.debug(f"Sentiment analysis: '{text[:50]}...' -> {result['label']} ({result['score']:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.5
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Convert to lowercase
        text = text.lower().strip()
        
        return text
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment analysis"""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            score = 0.0
            label = 'neutral'
            confidence = 0.5
        else:
            score = (positive_count - negative_count) / total_sentiment_words
            
            if score > 0.2:
                label = 'positive'
                confidence = min(0.9, 0.6 + abs(score) * 0.4)
            elif score < -0.2:
                label = 'negative'
                confidence = min(0.9, 0.6 + abs(score) * 0.4)
            else:
                label = 'neutral'
                confidence = 0.6
        
        return {
            'score': round(score, 3),
            'label': label,
            'confidence': round(confidence, 3)
        }
    
    async def get_sentiment_insights(self, brand_id: int, hours: int = 24) -> Dict[str, Any]:
        """Get sentiment insights for a brand"""
        from ..models.database import SessionLocal, Mention
        from datetime import timedelta
        
        db = SessionLocal()
        insights = {}
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            mentions = db.query(Mention).filter(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time,
                Mention.sentiment_label.isnot(None)
            ).all()
            
            if not mentions:
                return {
                    'total_mentions': 0,
                    'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'average_sentiment': 0.0,
                    'trend': 'stable'
                }
            
            # Calculate sentiment distribution - Extract actual Python values
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            total_score = 0
            
            for mention in mentions:
                label = getattr(mention, 'sentiment_label', 'neutral')  # type: ignore
                score = getattr(mention, 'sentiment_score', 0)  # type: ignore
                
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
                total_score += score or 0
            
            insights = {
                'total_mentions': len(mentions),
                'sentiment_breakdown': sentiment_counts,
                'average_sentiment': round(total_score / len(mentions), 3),
                'trend': 'improving' if total_score > 0 else 'declining' if total_score < -0.1 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment insights: {str(e)}")
            insights = {
                'total_mentions': 0,
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
                'average_sentiment': 0.0,
                'trend': 'stable'
            }
        finally:
            db.close()
        
        return insights