from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..models.database import get_db, Alert, Brand, Mention

router = APIRouter()
logger = logging.getLogger(__name__)

from pydantic import BaseModel

class AlertResponse(BaseModel):
    id: int
    brand_id: int
    alert_type: str
    title: str
    description: Optional[str]
    severity: str
    trigger_value: Optional[float]
    threshold_value: Optional[float]
    created_at: datetime
    is_read: bool
    is_resolved: bool
    
    class Config:
        from_attributes = True

@router.get("/{brand_id}", response_model=List[AlertResponse])
async def get_alerts(
    brand_id: int,
    limit: int = Query(50, description="Number of alerts to return"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    unread_only: bool = Query(False, description="Show only unread alerts"),
    db: Session = Depends(get_db)
):
    """Get alerts for a specific brand"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Build query
        query = db.query(Alert).filter(Alert.brand_id == brand_id)
        
        if severity:
            query = query.filter(Alert.severity == severity)
            
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
        
        return [
            AlertResponse(
                id=getattr(alert, 'id'),  # type: ignore
                brand_id=getattr(alert, 'brand_id'),  # type: ignore
                alert_type=str(getattr(alert, 'alert_type')),  # type: ignore
                title=str(getattr(alert, 'title')),  # type: ignore
                description=getattr(alert, 'description'),  # type: ignore
                severity=str(getattr(alert, 'severity')),  # type: ignore
                trigger_value=getattr(alert, 'trigger_value'),  # type: ignore
                threshold_value=getattr(alert, 'threshold_value'),  # type: ignore
                created_at=getattr(alert, 'created_at'),  # type: ignore
                is_read=getattr(alert, 'is_read'),  # type: ignore
                is_resolved=getattr(alert, 'is_resolved')  # type: ignore
            )
            for alert in alerts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alerts for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_read = True
        db.commit()
        
        return {"message": "Alert marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking alert {alert_id} as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark alert as read")

@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_resolved = True
        alert.is_read = True
        db.commit()
        
        return {"message": "Alert resolved"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve alert")

@router.get("/{brand_id}/summary")
async def get_alerts_summary(brand_id: int, db: Session = Depends(get_db)):
    """Get alert summary for a brand"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Count alerts by severity and status
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_alerts = db.query(Alert).filter(Alert.brand_id == brand_id).count()
        unread_alerts = db.query(Alert).filter(
            and_(Alert.brand_id == brand_id, Alert.is_read == False)
        ).count()
        
        today_alerts = db.query(Alert).filter(
            and_(
                Alert.brand_id == brand_id,
                Alert.created_at >= today
            )
        ).count()
        
        # Critical alerts in last 24h
        critical_alerts = db.query(Alert).filter(
            and_(
                Alert.brand_id == brand_id,
                Alert.severity == "critical",
                Alert.created_at >= datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        # Alerts by type
        alert_types = db.query(
            Alert.alert_type,
            func.count(Alert.id).label('count')
        ).filter(Alert.brand_id == brand_id).group_by(Alert.alert_type).all()
        
        alert_type_counts = {getattr(at, 'alert_type'): getattr(at, 'count') for at in alert_types}  # type: ignore
        
        return {
            "brand_id": brand_id,
            "brand_name": str(getattr(brand, 'name')),  # type: ignore
            "summary": {
                "total_alerts": total_alerts,
                "unread_alerts": unread_alerts,
                "today_alerts": today_alerts,
                "critical_alerts_24h": critical_alerts,
                "alert_types": alert_type_counts
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert summary for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alert summary")

@router.post("/{brand_id}/test")
async def create_test_alert(brand_id: int, db: Session = Depends(get_db)):
    """Create a test alert for demonstration"""
    try:
        # Verify brand exists
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Create test alert
        test_alert = Alert(
            brand_id=brand_id,
            alert_type="test",
            title=f"Test Alert for {getattr(brand, 'name')}",  # type: ignore
            description="This is a test alert to demonstrate the alert system functionality.",
            severity="medium",
            trigger_value=15.0,
            threshold_value=10.0
        )
        
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        
        logger.info(f"Created test alert for brand {getattr(brand, 'name')}")  # type: ignore
        
        return AlertResponse(
            id=getattr(test_alert, 'id'),  # type: ignore
            brand_id=getattr(test_alert, 'brand_id'),  # type: ignore
            alert_type=str(getattr(test_alert, 'alert_type')),  # type: ignore
            title=str(getattr(test_alert, 'title')),  # type: ignore
            description=getattr(test_alert, 'description'),  # type: ignore
            severity=str(getattr(test_alert, 'severity')),  # type: ignore
            trigger_value=getattr(test_alert, 'trigger_value'),  # type: ignore
            threshold_value=getattr(test_alert, 'threshold_value'),  # type: ignore
            created_at=getattr(test_alert, 'created_at'),  # type: ignore
            is_read=getattr(test_alert, 'is_read'),  # type: ignore
            is_resolved=getattr(test_alert, 'is_resolved')  # type: ignore
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating test alert for brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test alert")