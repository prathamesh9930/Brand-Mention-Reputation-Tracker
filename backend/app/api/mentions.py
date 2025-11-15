from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..models.database import get_db, Mention, Brand

router = APIRouter()
logger = logging.getLogger(__name__)

from pydantic import BaseModel

class MentionResponse(BaseModel):
    id: int
    brand_id: int
    content: str
    source: str
    source_url: Optional[str]
    author: Optional[str]
    created_at: datetime
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    confidence: Optional[float]
    likes: int
    shares: int
    comments: int
    
    class Config:
        from_attributes = True

@router.get("/{brand_id}", response_model=List[MentionResponse])
async def get_mentions(
    brand_id: int,
    limit: int = Query(100, description="Number of mentions to return"),
    offset: int = Query(0, description="Offset for pagination"),
    source: Optional[str] = Query(None, description="Filter by source (twitter, reddit, news, rss)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive, negative, neutral)"),
    hours: Optional[int] = Query(None, description="Get mentions from last N hours"),
    db: Session = Depends(get_db)
):
    """Get mentions for a specific brand"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Build query
        query = db.query(Mention).filter(Mention.brand_id == brand_id)
        
        # Apply filters
        if source:
            query = query.filter(Mention.source == source)
            
        if sentiment:
            query = query.filter(Mention.sentiment_label == sentiment)
            
        if hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(Mention.created_at >= cutoff_time)
        
        # Order by most recent and apply pagination
        mentions = query.order_by(desc(Mention.created_at)).offset(offset).limit(limit).all()
        
        return [
            MentionResponse(
                id=getattr(mention, 'id'),  # type: ignore
                brand_id=getattr(mention, 'brand_id'),  # type: ignore
                content=str(getattr(mention, 'content')),  # type: ignore
                source=str(getattr(mention, 'source')),  # type: ignore
                source_url=getattr(mention, 'source_url'),  # type: ignore
                author=getattr(mention, 'author'),  # type: ignore
                created_at=getattr(mention, 'created_at'),  # type: ignore
                sentiment_score=getattr(mention, 'sentiment_score'),  # type: ignore
                sentiment_label=getattr(mention, 'sentiment_label'),  # type: ignore
                confidence=getattr(mention, 'confidence'),  # type: ignore
                likes=getattr(mention, 'likes', 0) or 0,  # type: ignore
                shares=getattr(mention, 'shares', 0) or 0,  # type: ignore
                comments=getattr(mention, 'comments', 0) or 0  # type: ignore
            )
            for mention in mentions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mentions for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mentions")

@router.get("/{brand_id}/timeline")
async def get_mentions_timeline(
    brand_id: int,
    hours: int = Query(24, description="Time range in hours"),
    interval: str = Query("hour", description="Grouping interval (hour, day)"),
    db: Session = Depends(get_db)
):
    """Get mention timeline data for charts"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Group mentions by time interval
        if interval == "hour":
            # Group by hour
            time_groups = db.query(
                func.strftime('%Y-%m-%d %H:00:00', Mention.created_at).label('time_bucket'),
                func.count(Mention.id).label('mention_count'),
                func.avg(Mention.sentiment_score).label('avg_sentiment')
            ).filter(
                and_(
                    Mention.brand_id == brand_id,
                    Mention.created_at >= cutoff_time
                )
            ).group_by('time_bucket').all()
            
        else:  # day
            time_groups = db.query(
                func.date(Mention.created_at).label('time_bucket'),
                func.count(Mention.id).label('mention_count'),
                func.avg(Mention.sentiment_score).label('avg_sentiment')
            ).filter(
                and_(
                    Mention.brand_id == brand_id,
                    Mention.created_at >= cutoff_time
                )
            ).group_by('time_bucket').all()
        
        timeline_data = []
        for group in time_groups:
            timeline_data.append({
                "timestamp": getattr(group, 'time_bucket'),  # type: ignore
                "mention_count": getattr(group, 'mention_count'),  # type: ignore
                "average_sentiment": round(getattr(group, 'avg_sentiment') or 0, 3)  # type: ignore
            })
        
        return {
            "brand_id": brand_id,
            "brand_name": str(getattr(brand, 'name')),  # type: ignore
            "time_range_hours": hours,
            "interval": interval,
            "timeline": timeline_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching timeline for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mention timeline")

@router.get("/{brand_id}/sources")
async def get_mention_sources(
    brand_id: int,
    hours: int = Query(24, description="Time range in hours"),
    db: Session = Depends(get_db)
):
    """Get mention distribution by source"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        source_stats = db.query(
            Mention.source,
            func.count(Mention.id).label('mention_count'),
            func.avg(Mention.sentiment_score).label('avg_sentiment'),
            func.sum(Mention.likes).label('total_likes'),
            func.sum(Mention.shares).label('total_shares'),
            func.sum(Mention.comments).label('total_comments')
        ).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time
            )
        ).group_by(Mention.source).all()
        
        sources_data = []
        for stat in source_stats:
            sources_data.append({
                "source": getattr(stat, 'source'),  # type: ignore
                "mention_count": getattr(stat, 'mention_count'),  # type: ignore
                "average_sentiment": round(getattr(stat, 'avg_sentiment') or 0, 3),  # type: ignore
                "total_engagement": (getattr(stat, 'total_likes') or 0) + (getattr(stat, 'total_shares') or 0) + (getattr(stat, 'total_comments') or 0)  # type: ignore
            })
        
        return {
            "brand_id": brand_id,
            "brand_name": str(getattr(brand, 'name')),  # type: ignore
            "time_range_hours": hours,
            "sources": sources_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching source stats for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mention sources")

@router.get("/{brand_id}/trending")
async def get_trending_mentions(
    brand_id: int,
    limit: int = Query(10, description="Number of trending mentions to return"),
    hours: int = Query(24, description="Time range in hours"),
    db: Session = Depends(get_db)
):
    """Get trending mentions (high engagement)"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Calculate engagement score and get top mentions
        trending_mentions = db.query(Mention).filter(
            and_(
                Mention.brand_id == brand_id,
                Mention.created_at >= cutoff_time
            )
        ).all()
        
        # Sort by engagement (likes + shares + comments)
        trending_mentions.sort(
            key=lambda m: (getattr(m, 'likes', 0) or 0) + (getattr(m, 'shares', 0) or 0) + (getattr(m, 'comments', 0) or 0),  # type: ignore
            reverse=True
        )
        
        trending_data = []
        for mention in trending_mentions[:limit]:
            content = str(getattr(mention, 'content', ''))  # type: ignore
            engagement = (getattr(mention, 'likes', 0) or 0) + (getattr(mention, 'shares', 0) or 0) + (getattr(mention, 'comments', 0) or 0)  # type: ignore
            trending_data.append({
                "id": getattr(mention, 'id'),  # type: ignore
                "content": content[:200] + "..." if len(content) > 200 else content,
                "source": str(getattr(mention, 'source')),  # type: ignore
                "author": getattr(mention, 'author'),  # type: ignore
                "created_at": getattr(mention, 'created_at'),  # type: ignore
                "sentiment_score": getattr(mention, 'sentiment_score'),  # type: ignore
                "sentiment_label": getattr(mention, 'sentiment_label'),  # type: ignore
                "engagement_score": engagement,
                "source_url": getattr(mention, 'source_url')  # type: ignore
            })
        
        return {
            "brand_id": brand_id,
            "brand_name": str(getattr(brand, 'name')),  # type: ignore
            "time_range_hours": hours,
            "trending_mentions": trending_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trending mentions for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trending mentions")