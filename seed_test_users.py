#!/usr/bin/env python3
"""
Script to seed test users into the database
Run this after each database reset
"""

import sys
from pathlib import Path
import bcrypt

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.database import SessionLocal, init_db
from app.models import User, Portfolio
from datetime import datetime

def seed_test_users():
    """Seed test users into database"""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"✅ Database already has {existing_users} users. Skipping seeding.")
            return
        
        print("🌱 Seeding test users into database...\n")
        
        # Define test users
        test_users_data = [
            {
                "email": "demo@example.com",
                "password": "demo12345",
                "full_name": "Demo User",
                "is_premium": False
            },
            {
                "email": "trader@example.com",
                "password": "trader12345",
                "full_name": "John Trader",
                "is_premium": True
            },
            {
                "email": "investor@example.com",
                "password": "investor12345",
                "full_name": "Jane Investor",
                "is_premium": False
            }
        ]
        
        users = []
        for user_data in test_users_data:
            # Hash password using bcrypt
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(user_data["password"].encode('utf-8'), salt).decode('utf-8')
            
            user = User(
                email=user_data["email"],
                password_hash=hashed,
                full_name=user_data["full_name"],
                is_active=True,
                is_premium=user_data["is_premium"]
            )
            users.append(user)
            
            print(f"✅ Created user: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Full Name: {user_data['full_name']}")
            print(f"   Premium: {'Yes' if user_data['is_premium'] else 'No'}\n")
        
        # Add users to database
        db.add_all(users)
        db.commit()
        
        # Create portfolios for each user
        for user in users:
            portfolio = Portfolio(
                user_id=user.id,
                name="Main Portfolio",
                description=f"Main trading portfolio for {user.full_name}",
                starting_capital=50000.0,
                current_equity=52500.0,
                cash_balance=25000.0,
                is_active=True
            )
            db.add(portfolio)
        
        db.commit()
        
        print("=" * 70)
        print("✅ DATABASE SEEDED SUCCESSFULLY")
        print("=" * 70)
        print("\n📝 Test Credentials:\n")
        
        for i, user_data in enumerate(test_users_data, 1):
            print(f"{i}. Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}\n")
        
        print("🔐 Use these credentials to log in to the application.")
        print("📌 Remember: These are test accounts only. Change passwords in production!\n")
        
    except Exception as e:
        print(f"❌ Error seeding users: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    seed_test_users()
