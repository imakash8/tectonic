#!/usr/bin/env python3
"""
Database initialization script
Run this to create all tables in the database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models import User, Portfolio, Trade, Position, Watchlist, ActivityLog

def init_db():
    """Initialize database and create all tables"""
    print("🔄 Initializing database...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
        print("📊 Tables created:")
        print("   • users")
        print("   • portfolios")
        print("   • positions")
        print("   • trades")
        print("   • activity_logs")
        print("   • watchlists")
        print("\n✨ Your database is ready!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    init_db()
