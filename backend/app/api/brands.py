from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..models.database import get_db, Brand, Mention
from ..services.mention_collector import MentionCollector

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models for request/response
from pydantic import BaseModel

class BrandCreate(BaseModel):
    name: str
    keywords: Optional[List[str]] = []
    alert_threshold: Optional[int] = 10
    sentiment_threshold: Optional[float] = -0.5

class BrandResponse(BaseModel):
    id: int
    name: str
    keywords: List[str]
    created_at: datetime
    is_active: bool
    alert_threshold: int
    sentiment_threshold: float
    
    class Config:
        from_attributes = True

@router.post("/add", response_model=BrandResponse)
async def add_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    """Add a new brand to monitor"""
    try:
        # Check if brand already exists
        existing_brand = db.query(Brand).filter(Brand.name == brand.name).first()
        if existing_brand:
            raise HTTPException(status_code=400, detail=f"Brand '{brand.name}' already exists")
        
        # Create new brand
        db_brand = Brand(
            name=brand.name,
            keywords=brand.keywords or [],
            alert_threshold=brand.alert_threshold,
            sentiment_threshold=brand.sentiment_threshold
        )
        
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        
        logger.info(f"Added new brand: {brand.name}")
        
        return BrandResponse(
            id=getattr(db_brand, 'id'),  # type: ignore
            name=str(getattr(db_brand, 'name')),  # type: ignore
            keywords=getattr(db_brand, 'keywords') or [],  # type: ignore
            created_at=getattr(db_brand, 'created_at'),  # type: ignore
            is_active=getattr(db_brand, 'is_active'),  # type: ignore
            alert_threshold=getattr(db_brand, 'alert_threshold'),  # type: ignore
            sentiment_threshold=getattr(db_brand, 'sentiment_threshold')  # type: ignore
        )
        
    except Exception as e:
        logger.error(f"Error adding brand: {e}")
        raise HTTPException(status_code=500, detail="Failed to add brand")

@router.options("/add")
async def options_add_brand():
    """Handle CORS preflight for add brand endpoint"""
    return {"message": "OK"}

@router.get("/", response_model=List[BrandResponse])
async def get_brands(db: Session = Depends(get_db)):
    """Get all monitored brands"""
    try:
        brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        return [
            BrandResponse(
                id=getattr(brand, 'id'),  # type: ignore
                name=str(getattr(brand, 'name')),  # type: ignore
                keywords=getattr(brand, 'keywords') or [],  # type: ignore
                created_at=getattr(brand, 'created_at'),  # type: ignore
                is_active=getattr(brand, 'is_active'),  # type: ignore
                alert_threshold=getattr(brand, 'alert_threshold'),  # type: ignore
                sentiment_threshold=getattr(brand, 'sentiment_threshold')  # type: ignore
            )
            for brand in brands
        ]
        
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch brands")

@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get a specific brand by ID"""
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        return BrandResponse(
            id=getattr(brand, 'id'),  # type: ignore
            name=str(getattr(brand, 'name')),  # type: ignore
            keywords=getattr(brand, 'keywords') or [],  # type: ignore
            created_at=getattr(brand, 'created_at'),  # type: ignore
            is_active=getattr(brand, 'is_active'),  # type: ignore
            alert_threshold=getattr(brand, 'alert_threshold'),  # type: ignore
            sentiment_threshold=getattr(brand, 'sentiment_threshold')  # type: ignore
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch brand")

@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: int, brand_update: BrandCreate, db: Session = Depends(get_db)):
    """Update a brand's settings"""
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        brand.name = brand_update.name
        brand.keywords = brand_update.keywords or []
        brand.alert_threshold = brand_update.alert_threshold or 10
        brand.sentiment_threshold = brand_update.sentiment_threshold or -0.5
        
        db.commit()
        db.refresh(brand)
        
        logger.info(f"Updated brand: {brand.name}")
        
        return BrandResponse(
            id=getattr(brand, 'id'),  # type: ignore
            name=str(getattr(brand, 'name')),  # type: ignore
            keywords=getattr(brand, 'keywords') or [],  # type: ignore
            created_at=getattr(brand, 'created_at'),  # type: ignore
            is_active=getattr(brand, 'is_active'),  # type: ignore
            alert_threshold=getattr(brand, 'alert_threshold'),  # type: ignore
            sentiment_threshold=getattr(brand, 'sentiment_threshold')  # type: ignore
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update brand")

@router.delete("/{brand_id}")
async def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    """Delete/deactivate a brand"""
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Soft delete - just mark as inactive
        brand.is_active = False
        db.commit()
        
        logger.info(f"Deleted brand: {getattr(brand, 'name')}")  # type: ignore
        
        return {"message": f"Brand '{getattr(brand, 'name')}' has been deleted successfully"}  # type: ignore
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete brand")

@router.get("/{brand_id}/stats")
async def get_brand_stats(brand_id: int, db: Session = Depends(get_db)):
    """Get statistics for a brand"""
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Calculate stats from mentions
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        total_mentions = db.query(Mention).filter(Mention.brand_id == brand_id).count()
        
        today_mentions = db.query(Mention).filter(
            Mention.brand_id == brand_id,
            Mention.created_at >= today
        ).count()
        
        week_mentions = db.query(Mention).filter(
            Mention.brand_id == brand_id,
            Mention.created_at >= week_ago
        ).count()
        
        # Average sentiment - Extract actual Python values
        avg_sentiment_result = db.query(Mention).filter(
            Mention.brand_id == brand_id,
            Mention.sentiment_score.isnot(None)
        ).all()
        
        avg_sentiment = 0.0
        if avg_sentiment_result:
            sentiment_scores = []
            for m in avg_sentiment_result:
                score = getattr(m, 'sentiment_score', None)  # type: ignore
                if score is not None:
                    sentiment_scores.append(float(score))
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        return {
            "brand_id": brand_id,
            "brand_name": str(getattr(brand, 'name')),  # type: ignore
            "total_mentions": total_mentions,
            "today_mentions": today_mentions,
            "week_mentions": week_mentions,
            "average_sentiment": round(avg_sentiment, 3),
            "last_updated": now
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching brand stats {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch brand statistics")