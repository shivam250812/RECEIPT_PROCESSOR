"""
Database configuration and models for the OCR Receipt Processor.
Handles database connection, session management, and model definitions.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from typing import Generator
from contextlib import contextmanager

from .config import settings

# Database setup
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Receipt(Base):
    """Database model for receipt data."""
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    vendor = Column(String, nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)
    currency = Column(String, default="USD")
    billing_period = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    items_json = Column(Text, nullable=True)  # Store items as JSON
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Create indexes for optimized search performance
    __table_args__ = (
        Index('idx_vendor_amount', 'vendor', 'amount'),
        Index('idx_date_amount', 'transaction_date', 'amount'),
        Index('idx_category_amount', 'category', 'amount'),
        Index('idx_vendor_date', 'vendor', 'transaction_date'),
    )

def get_db() -> Generator:
    """Database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

def create_indexes():
    """Create additional indexes for performance optimization."""
    try:
        with engine.connect() as conn:
            # Full-text search index for vendor names
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_vendor_fts ON receipts(vendor)"))
            # Date range index
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_date_range ON receipts(transaction_date)"))
            # Amount range index
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_amount_range ON receipts(amount)"))
            # Confidence score index
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_confidence ON receipts(confidence_score)"))
            conn.commit()
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"❌ Error creating database indexes: {e}")
        raise

def reset_db():
    """Reset database (drop and recreate all tables)."""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database reset successfully")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        raise

def check_db_connection():
    """Check if database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False 