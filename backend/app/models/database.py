from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL (SQLite for development)
DATABASE_URL = "sqlite:///./brand_tracker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    keywords = Column(JSON)  # Additional keywords to monitor
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    alert_threshold = Column(Integer, default=10)  # Mentions per hour for alerts
    sentiment_threshold = Column(Float, default=-0.5)  # Negative sentiment threshold

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(50), nullable=False)  # twitter, reddit, news, rss
    source_url = Column(String(500))
    author = Column(String(100))
    platform_id = Column(String(100), unique=True)  # Original post ID
    created_at = Column(DateTime, nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Sentiment analysis results
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float)  # 0 to 1
    
    # Topic clustering
    topic_id = Column(Integer)
    topic_keywords = Column(JSON)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    reach = Column(Integer, default=0)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, index=True, nullable=False)
    alert_type = Column(String(50), nullable=False)  # spike, negative_sentiment, volume
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    trigger_value = Column(Float)
    threshold_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, index=True, nullable=False)
    keywords = Column(JSON, nullable=False)
    mentions_count = Column(Integer, default=0)
    avg_sentiment = Column(Float, default=0.0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

async def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()