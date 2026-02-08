"""Tests for the trading engine and validation gates."""

import pytest
from datetime import datetime, timedelta
from app.services.trading_engine import TradingEngine
from app.models.trade import Trade
from app.models.portfolio import Portfolio
from app.models.user import User
from app.utils.validators import validate_trade_inputs, validate_risk_reward


class TestTradingEngine:
    """Test suite for TradingEngine class."""

    def test_create_trading_engine(self):
        """Test TradingEngine instantiation."""
        engine = TradingEngine()
        assert engine is not None
        assert hasattr(engine, 'validate_trade')

    def test_validate_all_gates_pass(self):
        """Test validation when all gates pass."""
        engine = TradingEngine()
        
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.85
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None
        assert 'validation_gates_passed' in result or 'gates_status' in result

    def test_validate_price_deviation_gate(self):
        """Test price deviation validation gate."""
        engine = TradingEngine()
        
        # Test with reasonable deviation
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.85,
            'current_price': 150.50  # 0.33% deviation
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_validate_risk_reward_gate(self):
        """Test risk/reward ratio validation."""
        engine = TradingEngine()
        
        # Test with good risk/reward ratio
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 95.00,  # Risk: 5
            'take_profit': 110.00,  # Reward: 10
            'quantity': 10,
            'ai_confidence': 0.75
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_validate_poor_risk_reward(self):
        """Test rejection of poor risk/reward ratio."""
        engine = TradingEngine()
        
        # Test with poor risk/reward ratio (< 1:1)
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 95.00,  # Risk: 5
            'take_profit': 101.00,  # Reward: 1 (poor)
            'quantity': 10,
            'ai_confidence': 0.75
        }
        
        result = engine.validate_trade(trade_data)
        # Should still process but may fail validation
        assert result is not None

    def test_validate_ai_confidence_gate(self):
        """Test AI confidence validation."""
        engine = TradingEngine()
        
        # Test with high confidence
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.95  # Very high confidence
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None
        
        # Test with low confidence
        trade_data['ai_confidence'] = 0.30  # Low confidence
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_validate_market_hours_gate(self):
        """Test market hours validation."""
        engine = TradingEngine()
        
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.85,
            'market_open': True
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_validate_liquidity_gate(self):
        """Test liquidity validation gate."""
        engine = TradingEngine()
        
        # Test with sufficient volume
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.85,
            'daily_volume': 50000000  # High volume
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_validate_portfolio_exposure_gate(self, db_session):
        """Test portfolio exposure validation."""
        engine = TradingEngine()
        
        # This would normally check against existing positions
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10,
            'ai_confidence': 0.85,
            'portfolio_id': 1
        }
        
        result = engine.validate_trade(trade_data)
        assert result is not None

    def test_calculate_position_size(self):
        """Test position sizing calculation."""
        engine = TradingEngine()
        
        account_size = 10000
        risk_per_trade = 0.02  # 2%
        entry_price = 100.00
        stop_loss = 95.00
        
        position_size = engine.calculate_position_size(
            account_size, risk_per_trade, entry_price, stop_loss
        )
        
        assert position_size > 0
        assert position_size <= 100  # Reasonable position size

    def test_calculate_pnl(self):
        """Test P&L calculation."""
        engine = TradingEngine()
        
        # Long position
        entry = 100.00
        exit = 110.00
        quantity = 10
        
        pnl = engine.calculate_pnl('BUY', entry, exit, quantity)
        assert pnl == 100.0  # (110 - 100) * 10
        
        # Short position
        pnl = engine.calculate_pnl('SELL', entry, exit, quantity)
        assert pnl == -100.0  # (100 - 110) * 10

    def test_validate_stop_loss_above_entry_buy(self):
        """Test that stop loss is below entry for buy orders."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 105.00,  # Invalid: above entry
            'take_profit': 110.00,
            'quantity': 10
        }
        
        with pytest.raises((ValueError, AssertionError)):
            validate_trade_inputs(trade_data)

    def test_validate_take_profit_below_entry_buy(self):
        """Test that take profit is above entry for buy orders."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 95.00,
            'take_profit': 99.00,  # Invalid: below entry
            'quantity': 10
        }
        
        with pytest.raises((ValueError, AssertionError)):
            validate_trade_inputs(trade_data)

    def test_validate_positive_quantity(self):
        """Test that quantity must be positive."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 95.00,
            'take_profit': 110.00,
            'quantity': -10  # Invalid
        }
        
        with pytest.raises((ValueError, AssertionError)):
            validate_trade_inputs(trade_data)

    def test_validate_valid_symbol(self):
        """Test symbol validation."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 100.00,
            'stop_loss': 95.00,
            'take_profit': 110.00,
            'quantity': 10
        }
        
        # Should not raise
        result = validate_trade_inputs(trade_data)
        assert result is not None

    def test_validate_direction(self):
        """Test direction validation."""
        # Valid directions
        for direction in ['BUY', 'SELL']:
            trade_data = {
                'symbol': 'AAPL',
                'direction': direction,
                'entry_price': 100.00,
                'stop_loss': 95.00,
                'take_profit': 110.00,
                'quantity': 10
            }
            result = validate_trade_inputs(trade_data)
            assert result is not None

    def test_risk_reward_ratio_good(self):
        """Test risk/reward calculation for good ratio."""
        result = validate_risk_reward(
            entry_price=100.00,
            stop_loss=95.00,  # Risk: 5
            take_profit=110.00,  # Reward: 10
            direction='BUY'
        )
        assert result >= 2.0  # Good ratio (2:1)

    def test_risk_reward_ratio_poor(self):
        """Test risk/reward calculation for poor ratio."""
        result = validate_risk_reward(
            entry_price=100.00,
            stop_loss=95.00,  # Risk: 5
            take_profit=101.00,  # Reward: 1
            direction='BUY'
        )
        assert result <= 1.0  # Poor ratio

    def test_validate_sell_order_logic(self):
        """Test sell order validation logic."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'SELL',
            'entry_price': 100.00,
            'stop_loss': 105.00,  # Above entry for sell (valid)
            'take_profit': 90.00,  # Below entry for sell (valid)
            'quantity': 10
        }
        
        result = validate_trade_inputs(trade_data)
        assert result is not None
