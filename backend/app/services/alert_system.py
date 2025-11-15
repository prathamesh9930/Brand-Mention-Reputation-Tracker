import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class AlertSystem:
    """Intelligent alert system for detecting spikes and anomalies"""
    
    def __init__(self):
        self.spike_threshold_multiplier = 2.0  # Alert if mentions > 2x normal
        self.sentiment_threshold = -0.4  # Alert if sentiment drops below this
        self.volume_threshold = 10  # Minimum mentions for volume alerts
    
    async def check_for_alerts(self) -> List[Dict[str, Any]]:
        """Check for various types of alerts"""
        from ..models.database import SessionLocal, Brand
        
        new_alerts = []
        
        db = SessionLocal()
        try:
            # Get all active brands
            brands = db.query(Brand).filter(Brand.is_active == True).all()
            
            for brand in brands:
                try:
                    # Check different types of alerts
                    volume_alerts = await self._check_volume_spikes(brand, db)
                    sentiment_alerts = await self._check_sentiment_drops(brand, db)
                    engagement_alerts = await self._check_engagement_spikes(brand, db)
                    
                    # Combine all alerts
                    brand_alerts = volume_alerts + sentiment_alerts + engagement_alerts
                    
                    # Store alerts in database
                    for alert_data in brand_alerts:
                        await self._create_alert(alert_data, db)
                    
                    new_alerts.extend(brand_alerts)
                    
                except Exception as e:
                    logger.error(f"Error checking alerts for brand {brand.name}: {e}")
        
        finally:
            db.close()
        
        logger.info(f"Generated {len(new_alerts)} new alerts")
        return new_alerts
    
    async def _check_volume_spikes(self, brand, db) -> List[Dict[str, Any]]:
        """Check for unusual volume spikes in mentions"""
        from ..models.database import Mention
        from sqlalchemy import func, and_
        
        alerts = []
        
        try:
            now = datetime.utcnow()
            current_hour = now.replace(minute=0, second=0, microsecond=0)
            last_hour = current_hour - timedelta(hours=1)
            
            # Get mentions in current hour
            current_mentions = db.query(func.count(Mention.id)).filter(
                and_(
                    Mention.brand_id == brand.id,
                    Mention.created_at >= current_hour
                )
            ).scalar() or 0
            
            # Get average mentions per hour for last 24 hours (excluding current hour)
            day_ago = current_hour - timedelta(hours=24)
            
            hourly_counts = db.query(
                func.strftime('%Y-%m-%d %H', Mention.created_at).label('hour'),
                func.count(Mention.id).label('mention_count')
            ).filter(
                and_(
                    Mention.brand_id == brand.id,
                    Mention.created_at >= day_ago,
                    Mention.created_at < current_hour
                )
            ).group_by('hour').all()
            
            if not hourly_counts:
                return alerts
            
            # Calculate baseline average
            baseline_counts = [getattr(count, 'mention_count', 0) for count in hourly_counts]  # type: ignore
            avg_mentions = statistics.mean(baseline_counts) if baseline_counts else 0
            std_mentions = statistics.stdev(baseline_counts) if len(baseline_counts) > 1 else 0
            
            # Check for spike (mentions > threshold)
            threshold = max(
                brand.alert_threshold,  # User-defined threshold
                avg_mentions + (self.spike_threshold_multiplier * std_mentions)  # Statistical threshold
            )
            
            if current_mentions > threshold and current_mentions >= self.volume_threshold:
                severity = self._calculate_spike_severity(float(current_mentions), float(avg_mentions), float(threshold))
                
                alerts.append({
                    'brand_id': brand.id,
                    'alert_type': 'volume_spike',
                    'title': f'Mention Volume Spike Detected for {brand.name}',
                    'description': f'Unusual spike in mentions: {current_mentions} mentions in the last hour (normal: {avg_mentions:.1f}). This represents a {((current_mentions / max(avg_mentions, 1)) - 1) * 100:.0f}% increase.',
                    'severity': severity,
                    'trigger_value': float(current_mentions),
                    'threshold_value': float(threshold)
                })
                
                logger.warning(f"Volume spike alert for {brand.name}: {current_mentions} mentions (threshold: {threshold:.1f})")
        
        except Exception as e:
            logger.error(f"Error checking volume spikes for {brand.name}: {e}")
        
        return alerts
    
    async def _check_sentiment_drops(self, brand, db) -> List[Dict[str, Any]]:
        """Check for significant sentiment drops"""
        from ..models.database import Mention
        from sqlalchemy import func, and_
        
        alerts = []
        
        try:
            now = datetime.utcnow()
            
            # Get sentiment for last 2 hours
            recent_cutoff = now - timedelta(hours=2)
            
            recent_mentions = db.query(Mention).filter(
                and_(
                    Mention.brand_id == brand.id,
                    Mention.created_at >= recent_cutoff,
                    Mention.sentiment_score.isnot(None)
                )
            ).all()
            
            if len(recent_mentions) < 3:  # Need minimum data points
                return alerts
            
            recent_sentiment = statistics.mean([getattr(m, 'sentiment_score', 0) for m in recent_mentions])  # type: ignore
            
            # Get sentiment for previous 24 hours (excluding recent 2 hours)
            baseline_cutoff = now - timedelta(hours=26)
            baseline_end = recent_cutoff
            
            baseline_mentions = db.query(Mention).filter(
                and_(
                    Mention.brand_id == brand.id,
                    Mention.created_at >= baseline_cutoff,
                    Mention.created_at < baseline_end,
                    Mention.sentiment_score.isnot(None)
                )
            ).all()
            
            if baseline_mentions:
                baseline_sentiment = statistics.mean([getattr(m, 'sentiment_score', 0) for m in baseline_mentions])  # type: ignore
                sentiment_drop = baseline_sentiment - recent_sentiment
                
                # Check for significant drop or very negative sentiment
                if (recent_sentiment < brand.sentiment_threshold or 
                    (sentiment_drop > 0.3 and recent_sentiment < 0)):
                    
                    severity = 'critical' if recent_sentiment < -0.6 else 'high'
                    
                    # Count negative mentions
                    negative_count = len([m for m in recent_mentions if getattr(m, 'sentiment_score', 0) < -0.2])  # type: ignore
                    
                    alerts.append({
                        'brand_id': brand.id,
                        'alert_type': 'negative_sentiment',
                        'title': f'Negative Sentiment Alert for {brand.name}',
                        'description': f'Sentiment has dropped significantly. Current sentiment: {recent_sentiment:.2f}, Previous: {baseline_sentiment:.2f}. {negative_count} negative mentions detected in last 2 hours.',
                        'severity': severity,
                        'trigger_value': recent_sentiment,
                        'threshold_value': brand.sentiment_threshold
                    })
                    
                    logger.warning(f"Negative sentiment alert for {brand.name}: {recent_sentiment:.2f}")
        
        except Exception as e:
            logger.error(f"Error checking sentiment drops for {brand.name}: {e}")
        
        return alerts
    
    async def _check_engagement_spikes(self, brand, db) -> List[Dict[str, Any]]:
        """Check for unusual engagement spikes that might indicate viral content"""
        from ..models.database import Mention
        from sqlalchemy import and_
        
        alerts = []
        
        try:
            now = datetime.utcnow()
            recent_cutoff = now - timedelta(hours=6)
            
            # Get recent high-engagement mentions
            high_engagement_mentions = db.query(Mention).filter(
                and_(
                    Mention.brand_id == brand.id,
                    Mention.created_at >= recent_cutoff
                )
            ).all()
            
            if not high_engagement_mentions:
                return alerts
            
            # Calculate engagement scores
            engagement_scores = []
            viral_mentions = []
            
            for mention in high_engagement_mentions:
                engagement = (mention.likes or 0) + (mention.shares or 0) + (mention.comments or 0)
                engagement_scores.append(engagement)
                
                # Check if this mention is going viral (high engagement)
                if engagement > 100:  # Threshold for viral content
                    viral_mentions.append({
                        'mention': mention,
                        'engagement': engagement
                    })
            
            # Check for overall engagement spike
            if engagement_scores:
                avg_engagement = statistics.mean(engagement_scores)
                max_engagement = max(engagement_scores)
                
                if max_engagement > 500:  # Very high engagement threshold
                    alerts.append({
                        'brand_id': brand.id,
                        'alert_type': 'viral_content',
                        'title': f'Viral Content Detected for {brand.name}',
                        'description': f'A mention is gaining significant traction with {max_engagement} total engagements. Monitor for brand impact and consider response strategy.',
                        'severity': 'medium',
                        'trigger_value': max_engagement,
                        'threshold_value': 500
                    })
                    
                    logger.info(f"Viral content alert for {brand.name}: {max_engagement} engagements")
                
                elif len(viral_mentions) >= 3:  # Multiple viral mentions
                    total_viral_engagement = sum(vm['engagement'] for vm in viral_mentions)
                    
                    alerts.append({
                        'brand_id': brand.id,
                        'alert_type': 'engagement_spike',
                        'title': f'High Engagement Activity for {brand.name}',
                        'description': f'Multiple mentions are receiving high engagement ({len(viral_mentions)} posts with {total_viral_engagement} total engagements). Trending activity detected.',
                        'severity': 'medium',
                        'trigger_value': len(viral_mentions),
                        'threshold_value': 3
                    })
                    
                    logger.info(f"Engagement spike alert for {brand.name}: {len(viral_mentions)} viral mentions")
        
        except Exception as e:
            logger.error(f"Error checking engagement spikes for {brand.name}: {e}")
        
        return alerts
    
    def _calculate_spike_severity(self, current_value: float, baseline: float, threshold: float) -> str:
        """Calculate severity based on how much the spike exceeds normal levels"""
        if baseline == 0:
            baseline = 1  # Avoid division by zero
        
        spike_ratio = current_value / baseline
        
        if spike_ratio >= 5:
            return 'critical'
        elif spike_ratio >= 3:
            return 'high'
        elif spike_ratio >= 2:
            return 'medium'
        else:
            return 'low'
    
    async def _create_alert(self, alert_data: Dict[str, Any], db):
        """Create alert in database"""
        from ..models.database import Alert
        
        try:
            # Check if similar alert already exists in last hour
            recent_cutoff = datetime.utcnow() - timedelta(hours=1)
            
            existing_alert = db.query(Alert).filter(
                Alert.brand_id == alert_data['brand_id'],
                Alert.alert_type == alert_data['alert_type'],
                Alert.created_at >= recent_cutoff
            ).first()
            
            if existing_alert:
                # Update existing alert instead of creating duplicate
                existing_alert.trigger_value = alert_data['trigger_value']
                existing_alert.description = alert_data['description']
                existing_alert.severity = alert_data['severity']
                logger.info(f"Updated existing alert: {alert_data['title']}")
            else:
                # Create new alert
                alert = Alert(**alert_data)
                db.add(alert)
                db.commit()
                logger.info(f"Created new alert: {alert_data['title']}")
        
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            db.rollback()
    
    async def get_alert_trends(self, brand_id: int, days: int = 7) -> Dict[str, Any]:
        """Get alert trends and patterns for a brand"""
        from ..models.database import SessionLocal, Alert
        from sqlalchemy import func, and_
        
        db = SessionLocal()
        trends = {}
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get alerts by type and day
            alert_trends = db.query(
                func.date(Alert.created_at).label('date'),
                Alert.alert_type,
                Alert.severity,
                func.count(Alert.id).label('count')
            ).filter(
                and_(
                    Alert.brand_id == brand_id,
                    Alert.created_at >= cutoff_date
                )
            ).group_by('date', Alert.alert_type, Alert.severity).all()
            
            # Organize trends by date and type - Extract actual Python values
            daily_trends = defaultdict(lambda: defaultdict(int))
            severity_counts = defaultdict(int)
            
            for trend in alert_trends:
                date_str = str(getattr(trend, 'date', ''))  # type: ignore
                alert_type = getattr(trend, 'alert_type', '')  # type: ignore
                severity = getattr(trend, 'severity', '')  # type: ignore
                count = getattr(trend, 'count', 0)  # type: ignore
                
                daily_trends[date_str][alert_type] += count
                severity_counts[severity] += count
            
            trends = {
                'brand_id': brand_id,
                'time_range_days': days,
                'daily_trends': dict(daily_trends),
                'severity_distribution': dict(severity_counts),
                'total_alerts': sum(severity_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting alert trends: {e}")
        finally:
            db.close()
        
        return trends