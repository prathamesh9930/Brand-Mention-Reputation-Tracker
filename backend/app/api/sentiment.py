from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..models.database import get_db, Mention, Brand

router = APIRouter()
logger = logging.getLogger(__name__)

from pydantic import BaseModel

class SentimentAnalysisResponse(BaseModel):
    brand_id: int
    brand_name: str
    time_range_hours: int
    total_mentions: int
    sentiment_breakdown: dict
    sentiment_trend: List[dict]
    average_sentiment: float
    
class SentimentTimelineResponse(BaseModel):
    timestamp: str
    positive_count: int
    negative_count: int
    neutral_count: int
    average_score: float

@router.get("/{brand_id}/analysis")
async def get_sentiment_analysis(
    brand_id: int,
    hours: int = Query(24, description="Time range in hours"),
    db: Session = Depends(get_db)
):
    """Get comprehensive sentiment analysis for a brand"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get mentions in time range
        mentions_query = db.query(Mention).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time,
                Mention.sentiment_label.isnot(None)
            )
        )
        
        mentions = mentions_query.all()
        total_mentions = len(mentions)
        
        if total_mentions == 0:
            return SentimentAnalysisResponse(
                brand_id=brand_id,
                brand_name=str(brand.name),  # type: ignore
                time_range_hours=hours,
                total_mentions=0,
                sentiment_breakdown={"positive": 0, "negative": 0, "neutral": 0},
                sentiment_trend=[],
                average_sentiment=0.0
            )
        
        # Calculate sentiment breakdown
        sentiment_counts = db.query(
            Mention.sentiment_label,
            func.count(Mention.id).label('count')
        ).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time,
                Mention.sentiment_label.isnot(None)
            )
        ).group_by(Mention.sentiment_label).all()
        
        sentiment_breakdown = {"positive": 0, "negative": 0, "neutral": 0}
        for sentiment, count in sentiment_counts:
            if sentiment in sentiment_breakdown:
                sentiment_breakdown[sentiment] = count
        
        # Calculate average sentiment score - Extract actual Python values
        sentiment_scores = []
        for m in mentions:
            score = getattr(m, 'sentiment_score', None)  # type: ignore
            if score is not None:
                sentiment_scores.append(float(score))
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Get hourly sentiment trend
        sentiment_trend = db.query(
            func.strftime('%Y-%m-%d %H:00:00', Mention.created_at).label('hour'),
            func.count(func.case([(Mention.sentiment_label == 'positive', 1)])).label('positive_count'),
            func.count(func.case([(Mention.sentiment_label == 'negative', 1)])).label('negative_count'),
            func.count(func.case([(Mention.sentiment_label == 'neutral', 1)])).label('neutral_count'),
            func.avg(Mention.sentiment_score).label('avg_score')
        ).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time,
                Mention.sentiment_label.isnot(None)
            )
        ).group_by('hour').order_by('hour').all()
        
        trend_data = []
        for trend in sentiment_trend:
            trend_data.append({
                "timestamp": getattr(trend, 'hour', ''),  # type: ignore
                "positive_count": getattr(trend, 'positive_count', 0) or 0,  # type: ignore
                "negative_count": getattr(trend, 'negative_count', 0) or 0,  # type: ignore
                "neutral_count": getattr(trend, 'neutral_count', 0) or 0,  # type: ignore
                "average_score": round(getattr(trend, 'avg_score', 0) or 0, 3)  # type: ignore
            })
        
        return {
            "brand_id": brand_id,
            "brand_name": str(brand.name),  # type: ignore
            "time_range_hours": hours,
            "total_mentions": total_mentions,
            "sentiment_breakdown": sentiment_breakdown,
            "sentiment_trend": trend_data,
            "average_sentiment": round(avg_sentiment, 3)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sentiment analysis for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sentiment analysis")

@router.get("/{brand_id}/negative")
async def get_negative_mentions(
    brand_id: int,
    limit: int = Query(20, description="Number of negative mentions to return"),
    hours: int = Query(24, description="Time range in hours"),
    threshold: float = Query(-0.3, description="Sentiment threshold (more negative than this value)"),
    db: Session = Depends(get_db)
):
    """Get most negative mentions for review"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        negative_mentions = db.query(Mention).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time,
                Mention.sentiment_score <= threshold
            )
        ).order_by(Mention.sentiment_score.asc()).limit(limit).all()
        
        mentions_data = []
        for mention in negative_mentions:
            mentions_data.append({
                "id": mention.id,
                "content": mention.content,
                "source": mention.source,
                "author": mention.author,
                "created_at": mention.created_at,
                "sentiment_score": mention.sentiment_score,
                "sentiment_label": mention.sentiment_label,
                "confidence": mention.confidence,
                "source_url": mention.source_url,
                "engagement": {
                    "likes": mention.likes or 0,
                    "shares": mention.shares or 0,
                    "comments": mention.comments or 0
                }
            })
        
        return {
            "brand_id": brand_id,
            "brand_name": str(brand.name),  # type: ignore
            "time_range_hours": hours,
            "sentiment_threshold": threshold,
            "negative_mentions_count": len(mentions_data),
            "negative_mentions": mentions_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching negative mentions for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch negative mentions")

@router.get("/{brand_id}/comparison")
async def compare_sentiment_periods(
    brand_id: int,
    current_hours: int = Query(24, description="Current period in hours"),
    previous_hours: int = Query(24, description="Previous period in hours for comparison"),
    db: Session = Depends(get_db)
):
    """Compare sentiment between two time periods"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        now = datetime.utcnow()
        current_start = now - timedelta(hours=current_hours)
        previous_start = now - timedelta(hours=current_hours + previous_hours)
        previous_end = current_start
        
        # Current period stats
        current_mentions = db.query(Mention).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= current_start,
                Mention.sentiment_score.isnot(None)
            )
        ).all()
        
        # Previous period stats
        previous_mentions = db.query(Mention).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= previous_start,
                Mention.created_at < previous_end,
                Mention.sentiment_score.isnot(None)
            )
        ).all()
        
        def calculate_period_stats(mentions):
            if not mentions:
                return {
                    "total_mentions": 0,
                    "average_sentiment": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                }
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_sentiment = 0
            
            for mention in mentions:
                label = getattr(mention, 'sentiment_label', None)  # type: ignore
                score = getattr(mention, 'sentiment_score', 0)  # type: ignore
                
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
                total_sentiment += score or 0
            
            return {
                "total_mentions": len(mentions),
                "average_sentiment": round(total_sentiment / len(mentions), 3),
                "positive_count": sentiment_counts["positive"],
                "negative_count": sentiment_counts["negative"],
                "neutral_count": sentiment_counts["neutral"]
            }
        
        current_stats = calculate_period_stats(current_mentions)
        previous_stats = calculate_period_stats(previous_mentions)
        
        # Calculate changes
        sentiment_change = current_stats["average_sentiment"] - previous_stats["average_sentiment"]
        mention_change = current_stats["total_mentions"] - previous_stats["total_mentions"]
        
        return {
            "brand_id": brand_id,
            "brand_name": str(brand.name),  # type: ignore
            "comparison": {
                "current_period": {
                    "hours": current_hours,
                    "stats": current_stats
                },
                "previous_period": {
                    "hours": previous_hours,
                    "stats": previous_stats
                },
                "changes": {
                    "sentiment_change": round(sentiment_change, 3),
                    "mention_change": mention_change,
                    "sentiment_trend": "improving" if sentiment_change > 0.05 else "declining" if sentiment_change < -0.05 else "stable"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing sentiment periods for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare sentiment periods")