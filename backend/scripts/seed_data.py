"""
Database seeding script - populate with initial test data
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, init_db
from app.models import User, Portfolio, Trade, Position, ActivityLog
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with test data"""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(ActivityLog).delete()
        db.query(Trade).delete()
        db.query(Position).delete()
        db.query(Portfolio).delete()
        db.query(User).delete()
        
        print("🧹 Cleared existing data")
        
        # Create test users
        users = [
            User(
                email="demo@example.com",
                password_hash=hash_password("demo123"),
                full_name="Demo User",
                is_active=True,
                is_premium=False
            ),
            User(
                email="trader@example.com",
                password_hash=hash_password("trader123"),
                full_name="John Trader",
                is_active=True,
                is_premium=True
            ),
            User(
                email="investor@example.com",
                password_hash=hash_password("investor123"),
                full_name="Jane Investor",
                is_active=True,
                is_premium=False
            )
        ]
        
        db.add_all(users)
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Create portfolios
        portfolios = [
            Portfolio(
                user_id=users[0].id,
                name="Main Portfolio",
                description="Primary trading portfolio",
                starting_capital=50000.0,
                current_equity=52500.0,
                cash_balance=15000.0,
                is_active=True
            ),
            Portfolio(
                user_id=users[0].id,
                name="Crypto Portfolio",
                description="Bitcoin and Ethereum positions",
                starting_capital=10000.0,
                current_equity=11250.0,
                cash_balance=2000.0,
                is_active=True
            ),
            Portfolio(
                user_id=users[1].id,
                name="Growth Portfolio",
                description="High-growth tech stocks",
                starting_capital=100000.0,
                current_equity=118500.0,
                cash_balance=35000.0,
                is_active=True
            ),
            Portfolio(
                user_id=users[2].id,
                name="Dividend Portfolio",
                description="Dividend-focused stocks",
                starting_capital=75000.0,
                current_equity=73500.0,
                cash_balance=20000.0,
                is_active=True
            )
        ]
        
        db.add_all(portfolios)
        db.commit()
        print(f"✅ Created {len(portfolios)} portfolios")
        
        # Create closed trades (for analytics)
        closed_trades = [
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="AAPL",
                direction="BUY",
                entry_price=150.25,
                exit_price=165.75,
                stop_loss=145.00,
                take_profit=170.00,
                quantity=10,
                pnl=1550.0,
                pnl_percent=10.33,
                status="CLOSED",
                ai_confidence=0.85,
                entry_reasoning="Breakout above 150 resistance",
                opened_at=datetime.utcnow() - timedelta(days=30),
                closed_at=datetime.utcnow() - timedelta(days=20),
                close_reason="Take profit hit",
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="MSFT",
                direction="BUY",
                entry_price=380.00,
                exit_price=392.50,
                stop_loss=370.00,
                take_profit=400.00,
                quantity=5,
                pnl=625.0,
                pnl_percent=3.29,
                status="CLOSED",
                ai_confidence=0.78,
                entry_reasoning="Support bounce at 380",
                opened_at=datetime.utcnow() - timedelta(days=25),
                closed_at=datetime.utcnow() - timedelta(days=15),
                close_reason="Stop loss hit",
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="GOOGL",
                direction="SELL",
                entry_price=140.80,
                exit_price=138.50,
                stop_loss=145.00,
                take_profit=135.00,
                quantity=8,
                pnl=184.0,
                pnl_percent=1.63,
                status="CLOSED",
                ai_confidence=0.72,
                entry_reasoning="Resistance at 140",
                opened_at=datetime.utcnow() - timedelta(days=20),
                closed_at=datetime.utcnow() - timedelta(days=10),
                close_reason="Take profit hit",
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="TSLA",
                direction="BUY",
                entry_price=242.50,
                exit_price=235.00,
                stop_loss=240.00,
                take_profit=255.00,
                quantity=6,
                pnl=-45.0,
                pnl_percent=-1.85,
                status="CLOSED",
                ai_confidence=0.65,
                entry_reasoning="Moving average crossover",
                opened_at=datetime.utcnow() - timedelta(days=15),
                closed_at=datetime.utcnow() - timedelta(days=5),
                close_reason="Stop loss hit",
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="NVDA",
                direction="BUY",
                entry_price=875.25,
                exit_price=920.50,
                stop_loss=860.00,
                take_profit=950.00,
                quantity=2,
                pnl=890.5,
                pnl_percent=5.16,
                status="CLOSED",
                ai_confidence=0.88,
                entry_reasoning="Strong uptrend continuation",
                opened_at=datetime.utcnow() - timedelta(days=10),
                closed_at=datetime.utcnow() - timedelta(days=3),
                close_reason="Take profit hit",
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            )
        ]
        
        db.add_all(closed_trades)
        db.commit()
        print(f"✅ Created {len(closed_trades)} closed trades")
        
        # Create open trades
        open_trades = [
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="AMD",
                direction="BUY",
                entry_price=195.50,
                exit_price=None,
                stop_loss=190.00,
                take_profit=210.00,
                quantity=12,
                pnl=None,
                pnl_percent=None,
                status="OPEN",
                ai_confidence=0.81,
                entry_reasoning="Breakout above 195",
                opened_at=datetime.utcnow() - timedelta(days=2),
                closed_at=None,
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="META",
                direction="BUY",
                entry_price=520.00,
                exit_price=None,
                stop_loss=510.00,
                take_profit=540.00,
                quantity=4,
                pnl=None,
                pnl_percent=None,
                status="OPEN",
                ai_confidence=0.76,
                entry_reasoning="Technical bounce setup",
                opened_at=datetime.utcnow() - timedelta(days=1),
                closed_at=None,
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            ),
            Trade(
                portfolio_id=portfolios[0].id,
                symbol="NFLX",
                direction="SELL",
                entry_price=385.75,
                exit_price=None,
                stop_loss=395.00,
                take_profit=370.00,
                quantity=7,
                pnl=None,
                pnl_percent=None,
                status="OPEN",
                ai_confidence=0.73,
                entry_reasoning="Overbought condition",
                opened_at=datetime.utcnow(),
                closed_at=None,
                validation_gates_passed={
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                    "gate_6": {"passed": True},
                    "gate_7": {"passed": True},
                    "gate_8": {"passed": True},
                    "gate_9": {"passed": True}
                }
            )
        ]
        
        db.add_all(open_trades)
        db.commit()
        print(f"✅ Created {len(open_trades)} open trades")
        
        # Create positions
        positions = [
            Position(
                portfolio_id=portfolios[0].id,
                symbol="AAPL",
                direction="BUY",
                entry_price=165.75,
                stop_loss=160.00,
                take_profit=175.00,
                quantity=10,
                ai_confidence=0.85,
                entry_reasoning="Trend continuation",
                opened_at=datetime.utcnow() - timedelta(days=20),
                validation_gates_passed={"all_gates": "passed"}
            ),
            Position(
                portfolio_id=portfolios[0].id,
                symbol="MSFT",
                direction="BUY",
                entry_price=392.50,
                stop_loss=385.00,
                take_profit=405.00,
                quantity=5,
                ai_confidence=0.78,
                entry_reasoning="Support bounce",
                opened_at=datetime.utcnow() - timedelta(days=15),
                validation_gates_passed={"all_gates": "passed"}
            ),
            Position(
                portfolio_id=portfolios[1].id,
                symbol="BTC",
                direction="BUY",
                entry_price=42500.00,
                stop_loss=40000.00,
                take_profit=50000.00,
                quantity=1,
                ai_confidence=0.82,
                entry_reasoning="Bullish pattern",
                opened_at=datetime.utcnow() - timedelta(days=30),
                validation_gates_passed={"all_gates": "passed"}
            ),
            Position(
                portfolio_id=portfolios[1].id,
                symbol="ETH",
                direction="BUY",
                entry_price=2500.00,
                stop_loss=2300.00,
                take_profit=2800.00,
                quantity=5,
                ai_confidence=0.79,
                entry_reasoning="Accumulation zone",
                opened_at=datetime.utcnow() - timedelta(days=20),
                validation_gates_passed={"all_gates": "passed"}
            )
        ]
        
        db.add_all(positions)
        db.commit()
        print(f"✅ Created {len(positions)} open positions")
        
        # Create activity logs
        activity_logs = [
            ActivityLog(
                trade_id=closed_trades[0].id,
                event_type="EXECUTED",
                reason="Trade executed successfully",
                details={"entry_price": 150.25, "quantity": 10}
            ),
            ActivityLog(
                trade_id=closed_trades[0].id,
                event_type="CLOSED",
                reason="Take profit hit at 165.75",
                details={"exit_price": 165.75, "pnl": 1550.0}
            ),
            ActivityLog(
                trade_id=closed_trades[1].id,
                event_type="EXECUTED",
                reason="Trade executed successfully",
                details={"entry_price": 380.00, "quantity": 5}
            ),
            ActivityLog(
                trade_id=closed_trades[1].id,
                event_type="CLOSED",
                reason="Stop loss hit at 370.00",
                details={"exit_price": 392.50, "pnl": 625.0}
            )
        ]
        
        db.add_all(activity_logs)
        db.commit()
        print(f"✅ Created {len(activity_logs)} activity logs")
        
        print("\n✨ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Portfolios: {len(portfolios)}")
        print(f"  - Closed Trades: {len(closed_trades)}")
        print(f"  - Open Trades: {len(open_trades)}")
        print(f"  - Open Positions: {len(positions)}")
        print(f"  - Activity Logs: {len(activity_logs)}")
        
        print(f"\n🔐 Test Credentials:")
        for i, user in enumerate(users, 1):
            print(f"  User {i}: {user.email} / demo123 (change 'demo123' with actual password)")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
