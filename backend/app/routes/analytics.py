"""
Analytics routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Portfolio, Trade, User
from app.routes.auth import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/overview")
async def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio analytics overview"""
    try:
        # Get user's portfolios only
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
        
        total_capital = sum(p.starting_capital for p in portfolios)
        total_equity = sum(p.current_equity for p in portfolios)
        total_pnl = total_equity - total_capital
        total_return_pct = (total_pnl / total_capital * 100) if total_capital > 0 else 0
        
        # Get trade statistics for user's portfolios (join through portfolio)
        all_trades = db.query(Trade).join(Portfolio).filter(Portfolio.user_id == current_user.id).all()
        closed_trades = [t for t in all_trades if t.status == "CLOSED"]
        total_trades = len(all_trades)
        winning_trades = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
        losing_trades = sum(1 for t in closed_trades if t.pnl and t.pnl <= 0)
        
        total_gross_profit = sum(t.pnl for t in closed_trades if t.pnl and t.pnl > 0)
        total_gross_loss = sum(abs(t.pnl) for t in closed_trades if t.pnl and t.pnl < 0)
        profit_factor = (total_gross_profit / total_gross_loss) if total_gross_loss > 0 else 0
        
        avg_win = (total_gross_profit / winning_trades) if winning_trades > 0 else 0
        avg_loss = (total_gross_loss / losing_trades) if losing_trades > 0 else 0
        
        win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0
        
        return {
            "total_capital": total_capital,
            "total_equity": total_equity,
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "portfolios_count": len(portfolios),
            "total_trades": total_trades,
            "closed_trades": len(closed_trades),
            "open_trades": total_trades - len(closed_trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": ((win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)) if closed_trades else 0
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/performance")
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance metrics"""
    try:
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
        
        performance_data = []
        for portfolio in portfolios:
            closed_trades = [t for t in portfolio.trades if t.status == "CLOSED"]
            
            if closed_trades:
                monthly_pnl = {}
                for trade in closed_trades:
                    if trade.closed_at:
                        month_key = trade.closed_at.strftime("%Y-%m")
                        if month_key not in monthly_pnl:
                            monthly_pnl[month_key] = 0
                        monthly_pnl[month_key] += trade.pnl or 0
                
                performance_data.append({
                    "portfolio_id": portfolio.id,
                    "portfolio_name": portfolio.name,
                    "closed_trades": len(closed_trades),
                    "total_pnl": sum(t.pnl for t in closed_trades if t.pnl),
                    "monthly_pnl": monthly_pnl,
                    "best_trade": max((t.pnl for t in closed_trades if t.pnl), default=0),
                    "worst_trade": min((t.pnl for t in closed_trades if t.pnl), default=0)
                })
        
        return performance_data
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/comprehensive")
async def get_comprehensive_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics with advanced metrics"""
    try:
        all_trades = db.query(Trade).join(Portfolio).filter(Portfolio.user_id == current_user.id).all()
        closed_trades = [t for t in all_trades if t.status == "CLOSED"]
        
        if not closed_trades:
            return {
                "status": "insufficient_data",
                "message": "Minimum 5 closed trades required for analysis",
                "trades_count": 0
            }
        
        # Calculate win/loss streaks
        winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl and t.pnl <= 0]
        
        # Sorted by time
        sorted_trades = sorted(closed_trades, key=lambda t: t.closed_at or datetime.utcnow())
        
        current_streak = 1
        max_win_streak = 1
        max_loss_streak = 1
        current_win_streak = 1
        current_loss_streak = 1
        
        for i in range(1, len(sorted_trades)):
            prev_win = sorted_trades[i-1].pnl and sorted_trades[i-1].pnl > 0
            curr_win = sorted_trades[i].pnl and sorted_trades[i].pnl > 0
            
            if curr_win == prev_win:
                current_streak += 1
                if curr_win:
                    current_win_streak = current_streak
                    max_win_streak = max(max_win_streak, current_win_streak)
                else:
                    current_loss_streak = current_streak
                    max_loss_streak = max(max_loss_streak, current_loss_streak)
            else:
                current_streak = 1
        
        # Expectancy calculation
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        
        # Profit factor
        total_profit = sum(t.pnl for t in winning_trades if t.pnl)
        total_loss = abs(sum(t.pnl for t in losing_trades if t.pnl))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # System grade (A+ to F based on metrics)
        grade_score = 0
        grade_score += (win_rate * 30)  # Win rate (30 pts)
        grade_score += min(profit_factor * 10, 25)  # Profit factor (25 pts)
        grade_score += min(expectancy / 10, 25)  # Expectancy (25 pts)
        grade_score += min(len(closed_trades) / 2, 20)  # Trade count (20 pts)
        
        if grade_score >= 95:
            grade = "A+"
        elif grade_score >= 90:
            grade = "A"
        elif grade_score >= 85:
            grade = "A-"
        elif grade_score >= 80:
            grade = "B+"
        elif grade_score >= 70:
            grade = "B"
        elif grade_score >= 60:
            grade = "C"
        elif grade_score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        # Daily metrics (last 7, 30, 90 days)
        now = datetime.utcnow()
        days_7_ago = now - timedelta(days=7)
        days_30_ago = now - timedelta(days=30)
        days_90_ago = now - timedelta(days=90)
        
        trades_7d = [t for t in closed_trades if t.closed_at and t.closed_at >= days_7_ago]
        trades_30d = [t for t in closed_trades if t.closed_at and t.closed_at >= days_30_ago]
        trades_90d = [t for t in closed_trades if t.closed_at and t.closed_at >= days_90_ago]
        
        def calculate_metrics(trades):
            if not trades:
                return None
            wins = [t for t in trades if t.pnl and t.pnl > 0]
            wr = len(wins) / len(trades) if trades else 0
            pf = sum(t.pnl for t in wins if t.pnl) / abs(sum(t.pnl for t in trades if t.pnl and t.pnl < 0)) if any(t.pnl < 0 for t in trades) else 0
            return {
                "trade_count": len(trades),
                "win_rate": wr * 100,
                "profit_factor": pf,
                "total_pnl": sum(t.pnl for t in trades if t.pnl)
            }
        
        return {
            "status": "complete",
            "total_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_pct": win_rate * 100,
            "profit_factor": round(profit_factor, 2),
            "expectancy": round(expectancy, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_win_streak": max_win_streak,
            "max_loss_streak": max_loss_streak,
            "system_grade": grade,
            "grade_score": round(grade_score, 1),
            "metrics_7d": calculate_metrics(trades_7d),
            "metrics_30d": calculate_metrics(trades_30d),
            "metrics_90d": calculate_metrics(trades_90d)
        }
    except Exception as e:
        logger.error(f"Error fetching comprehensive analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
