#!/usr/bin/env python3
"""
Database setup script for the OCR Receipt Processor.
Initializes database tables and creates indexes for optimal performance.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import init_db, create_indexes, check_db_connection
from app.core.config import settings

def main():
    """Main setup function."""
    print("🔧 Setting up OCR Receipt Processor Database")
    print("=" * 50)
    
    try:
        # Check if database directory exists
        os.makedirs("data", exist_ok=True)
        print("✅ Data directory created/verified")
        
        # Initialize database tables
        print("📊 Creating database tables...")
        init_db()
        
        # Create performance indexes
        print("⚡ Creating database indexes...")
        create_indexes()
        
        # Test database connection
        print("🔍 Testing database connection...")
        if check_db_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        print("\n🎉 Database setup completed successfully!")
        print("=" * 50)
        print("📁 Database location: data/receipts.db")
        print("🔗 Database URL: " + settings.DATABASE_URL)
        print("\n🚀 You can now start the application with:")
        print("   python scripts/start_system.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 