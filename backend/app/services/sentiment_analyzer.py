import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """AI-powered sentiment analysis service"""
    
    def __init__(self):
        self.model_loaded = False
        self.vectorizer = None
        self.sentiment_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models"""
        try:
            # For demo purposes, we'll use a simple rule-based approach
            # In production, load pre-trained transformers model
            
            # Simple keyword-based sentiment analysis for demo
            self.positive_words = [
                'love', 'amazing', 'great', 'excellent', 'fantastic', 'wonderful',
                'best', 'awesome', 'perfect', 'incredible', 'outstanding', 'brilliant',
                'superb', 'marvelous', 'terrific', 'exceptional', 'remarkable',
                'pleased', 'satisfied', 'happy', 'delighted', 'impressed', 'recommend'
            ]
            
            self.negative_words = [
                'hate', 'terrible', 'awful', 'bad', 'worst', 'horrible', 'disgusting',
                'pathetic', 'useless', 'disappointing', 'frustrated', 'angry', 'annoyed',
                'dissatisfied', 'unhappy', 'complaint', 'problem', 'issue', 'bug',
                'broken', 'failed', 'error', 'crash', 'slow', 'expensive', 'overpriced'
            ]
            
            # Simple word counting for basic topic analysis
            self.topic_words = set()
            
            self.model_loaded = True
            logger.info("Sentiment analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
    
    async def process_pending_mentions(self) -> List[Dict[str, Any]]:
        """Process mentions that need sentiment analysis"""
        from ..models.database import SessionLocal, Mention
        
        db = SessionLocal()
        processed_mentions = []
        
        try:
            # Get mentions without sentiment analysis
            pending_mentions = db.query(Mention).filter(
                Mention.sentiment_score.is_(None)
            ).limit(50).all()  # Process in batches
            
            if not pending_mentions:
                return processed_mentions
            
            logger.info(f"Processing sentiment for {len(pending_mentions)} mentions")
            
            for mention in pending_mentions:
                try:
                    # Analyze sentiment - ensure we get the actual string content
                    content_text = str(mention.content)  # type: ignore
                    sentiment_result = await self.analyze_sentiment(content_text)
                    
                    # Update mention with sentiment data
                    mention.sentiment_score = sentiment_result['score']
                    mention.sentiment_label = sentiment_result['label']
                    mention.confidence = sentiment_result['confidence']
                    
                    # Add to processed list for real-time updates
                    processed_mentions.append({
                        'id': mention.id,
                        'brand_id': mention.brand_id,
                        'content': str(mention.content),  # type: ignore
                        'sentiment_score': mention.sentiment_score,
                        'sentiment_label': mention.sentiment_label,
                        'confidence': mention.confidence,
                        'source': str(mention.source),  # type: ignore
                        'created_at': mention.created_at
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing sentiment for mention {mention.id}: {e}")
            
            db.commit()
            
            # Perform topic clustering for processed mentions
            if processed_mentions:
                await self._perform_simple_topic_analysis(processed_mentions, db)
            
            logger.info(f"Successfully processed sentiment for {len(processed_mentions)} mentions")
            
        except Exception as e:
            logger.error(f"Error in sentiment processing: {e}")
            db.rollback()
        finally:
            db.close()
        
        return processed_mentions
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        try:
            if not self.model_loaded:
                self._initialize_models()
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Simple rule-based sentiment analysis for demo
            # In production, use transformers model like BERT, RoBERTa, etc.
            sentiment_result = self._rule_based_sentiment(cleaned_text)
            
            return sentiment_result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
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
            score = (positive_count - negative_count) / len(words)
            # Normalize score to -1 to 1 range
            score = max(-1.0, min(1.0, score * 5))  # Amplify the score
            
            if score > 0.1:
                label = 'positive'
            elif score < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Confidence based on number of sentiment words
            confidence = min(0.9, 0.5 + (total_sentiment_words * 0.1))
        
        return {
            'score': round(score, 3),
            'label': label,
            'confidence': round(confidence, 3)
        }
    
    async def _perform_simple_topic_analysis(self, mentions: List[Dict[str, Any]], db):
        """Perform simple topic analysis using word frequency"""
        try:
            if len(mentions) < 3:
                return
            
            # Extract common words from all mentions
            all_words = []
            for mention in mentions:
                cleaned_text = self._clean_text(mention['content'])
                words = [word for word in cleaned_text.split() if len(word) > 3]
                all_words.extend(words)
            
            # Get most common words as topics
            word_counts = Counter(all_words)
            common_words = [word for word, count in word_counts.most_common(10)]
            
            # Assign simple topic to mentions based on word presence
            for i, mention in enumerate(mentions):
                mention_words = set(self._clean_text(mention['content']).split())
                topic_words = [word for word in common_words if word in mention_words]
                
                # Simple topic assignment
                topic_id = hash(','.join(sorted(topic_words[:3]))) % 5
                
                logger.debug(f"Assigned topic {topic_id} to mention {mention['id']}")
            
            logger.info(f"Performed simple topic analysis for {len(mentions)} mentions")
            
        except Exception as e:
            logger.error(f"Error in topic analysis: {e}")
    
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
                Mention.sentiment_score.isnot(None)
            ).all()
            
            if not mentions:
                return {
                    'brand_id': brand_id,
                    'insights': 'No recent mentions with sentiment data',
                    'recommendations': []
                }
            
            # Calculate insights - Extract actual Python values from SQLAlchemy objects
            sentiments = []
            for m in mentions:
                score = getattr(m, 'sentiment_score', None)  # type: ignore
                if score is not None:
                    sentiments.append(score)
            
            if not sentiments:
                return {
                    'brand_id': brand_id,
                    'insights': 'No recent mentions with sentiment data',
                    'recommendations': []
                }
            
            avg_sentiment = statistics.mean(sentiments)
            sentiment_trend = 'improving' if avg_sentiment > 0.1 else 'declining' if avg_sentiment < -0.1 else 'stable'
            
            # Count by sentiment
            positive_count = len([s for s in sentiments if s > 0.1])
            negative_count = len([s for s in sentiments if s < -0.1])
            neutral_count = len(sentiments) - positive_count - negative_count
            
            # Get most negative mentions for attention
            negative_mentions = []
            for m in mentions:
                score = getattr(m, 'sentiment_score', None)  # type: ignore
                if score is not None and score < -0.3:
                    negative_mentions.append(m)
            negative_mentions.sort(key=lambda x: getattr(x, 'sentiment_score', 0))
            
            recommendations = []
            
            if negative_count > positive_count:
                recommendations.append("Consider addressing negative feedback immediately")
            
            if len(negative_mentions) > 5:
                recommendations.append("High volume of negative sentiment detected - urgent attention needed")
            
            if avg_sentiment > 0.5:
                recommendations.append("Positive sentiment momentum - consider amplifying positive content")
            
            insights = {
                'brand_id': brand_id,
                'time_range_hours': hours,
                'total_mentions': len(mentions),
                'average_sentiment': round(avg_sentiment, 3),
                'sentiment_distribution': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count
                },
                'sentiment_trend': sentiment_trend,
                'urgent_negative_mentions': len(negative_mentions),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating sentiment insights: {e}")
        finally:
            db.close()
        
        return insights