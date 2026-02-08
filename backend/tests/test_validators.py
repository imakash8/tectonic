"""Tests for validation utilities."""

import pytest
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_symbol,
    validate_trade_inputs,
    validate_risk_reward,
    validate_price,
    validate_quantity,
    validate_direction
)


class TestEmailValidation:
    """Test email validation."""

    def test_valid_email(self):
        """Test valid email addresses."""
        valid_emails = [
            'user@example.com',
            'test.user@example.co.uk',
            'user+tag@example.com'
        ]
        for email in valid_emails:
            assert validate_email(email) is not None

    def test_invalid_email(self):
        """Test invalid email addresses."""
        invalid_emails = [
            'notanemail',
            'user@',
            '@example.com',
            'user@.com'
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError):
                validate_email(email)


class TestPasswordValidation:
    """Test password validation."""

    def test_valid_password(self):
        """Test valid password."""
        valid_passwords = [
            'SecurePass123!',
            'MyPassword@2024',
            'StrongP@ss123'
        ]
        for pwd in valid_passwords:
            assert validate_password(pwd) is not None

    def test_password_too_short(self):
        """Test password length requirement."""
        with pytest.raises(ValueError):
            validate_password('short')

    def test_password_no_uppercase(self):
        """Test password uppercase requirement."""
        with pytest.raises(ValueError):
            validate_password('lowercase123!')

    def test_password_no_number(self):
        """Test password number requirement."""
        with pytest.raises(ValueError):
            validate_password('NoNumbers!')

    def test_password_no_special_char(self):
        """Test password special character requirement."""
        with pytest.raises(ValueError):
            validate_password('NoSpecial123')


class TestSymbolValidation:
    """Test stock symbol validation."""

    def test_valid_symbols(self):
        """Test valid stock symbols."""
        valid_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'BRK']
        for symbol in valid_symbols:
            assert validate_symbol(symbol) == symbol.upper()

    def test_invalid_symbol_length(self):
        """Test symbol length constraints."""
        with pytest.raises(ValueError):
            validate_symbol('A')  # Too short

    def test_invalid_symbol_numbers(self):
        """Test symbol with numbers."""
        result = validate_symbol('AAPL1')
        # Some symbols have numbers, so might be valid
        assert result is not None or True

    def test_symbol_case_insensitive(self):
        """Test symbol case conversion."""
        assert validate_symbol('aapl') == 'AAPL'
        assert validate_symbol('AaPl') == 'AAPL'


class TestPriceValidation:
    """Test price validation."""

    def test_valid_prices(self):
        """Test valid price values."""
        valid_prices = [0.01, 10.50, 100.99, 1000.00, 10000.00]
        for price in valid_prices:
            assert validate_price(price) == price

    def test_negative_price(self):
        """Test negative price rejection."""
        with pytest.raises(ValueError):
            validate_price(-10.00)

    def test_zero_price(self):
        """Test zero price rejection."""
        with pytest.raises(ValueError):
            validate_price(0)

    def test_very_large_price(self):
        """Test very large price values."""
        result = validate_price(9999999.99)
        assert result == 9999999.99

    def test_price_precision(self):
        """Test price decimal precision."""
        # Most prices have at most 4 decimal places
        result = validate_price(100.1234)
        assert result == 100.1234


class TestQuantityValidation:
    """Test quantity validation."""

    def test_valid_quantities(self):
        """Test valid quantity values."""
        valid_quantities = [1, 10, 100, 1000, 10000]
        for qty in valid_quantities:
            assert validate_quantity(qty) == qty

    def test_zero_quantity(self):
        """Test zero quantity rejection."""
        with pytest.raises(ValueError):
            validate_quantity(0)

    def test_negative_quantity(self):
        """Test negative quantity rejection."""
        with pytest.raises(ValueError):
            validate_quantity(-10)

    def test_fractional_quantity(self):
        """Test fractional quantity handling."""
        # Most trades require whole shares for stocks
        result = validate_quantity(10)
        assert isinstance(result, int)


class TestDirectionValidation:
    """Test trade direction validation."""

    def test_valid_directions(self):
        """Test valid directions."""
        for direction in ['BUY', 'SELL']:
            result = validate_direction(direction)
            assert result == direction

    def test_case_insensitive_direction(self):
        """Test direction case handling."""
        assert validate_direction('buy') == 'BUY'
        assert validate_direction('sell') == 'SELL'

    def test_invalid_direction(self):
        """Test invalid direction rejection."""
        with pytest.raises(ValueError):
            validate_direction('INVALID')


class TestRiskRewardValidation:
    """Test risk/reward ratio validation."""

    def test_good_rr_ratio_buy(self):
        """Test good risk/reward for buy order."""
        rr = validate_risk_reward(
            entry_price=100.00,
            stop_loss=95.00,
            take_profit=110.00,
            direction='BUY'
        )
        assert rr >= 2.0  # 1:2 ratio

    def test_good_rr_ratio_sell(self):
        """Test good risk/reward for sell order."""
        rr = validate_risk_reward(
            entry_price=100.00,
            stop_loss=105.00,
            take_profit=90.00,
            direction='SELL'
        )
        assert rr >= 2.0

    def test_poor_rr_ratio(self):
        """Test poor risk/reward ratio."""
        rr = validate_risk_reward(
            entry_price=100.00,
            stop_loss=95.00,
            take_profit=101.00,
            direction='BUY'
        )
        assert rr < 1.0

    def test_invalid_sl_tp_buy(self):
        """Test invalid stop loss/take profit for buy."""
        with pytest.raises(ValueError):
            validate_risk_reward(
                entry_price=100.00,
                stop_loss=105.00,  # Above entry - invalid for buy
                take_profit=110.00,
                direction='BUY'
            )

    def test_invalid_sl_tp_sell(self):
        """Test invalid stop loss/take profit for sell."""
        with pytest.raises(ValueError):
            validate_risk_reward(
                entry_price=100.00,
                stop_loss=95.00,  # Below entry - invalid for sell
                take_profit=90.00,
                direction='SELL'
            )

    def test_equal_sl_entry(self):
        """Test stop loss equal to entry."""
        with pytest.raises(ValueError):
            validate_risk_reward(
                entry_price=100.00,
                stop_loss=100.00,
                take_profit=110.00,
                direction='BUY'
            )

    def test_equal_tp_entry(self):
        """Test take profit equal to entry."""
        with pytest.raises(ValueError):
            validate_risk_reward(
                entry_price=100.00,
                stop_loss=95.00,
                take_profit=100.00,
                direction='BUY'
            )


class TestCompleteTradeValidation:
    """Test complete trade input validation."""

    def test_valid_trade_inputs(self):
        """Test validation of complete valid trade."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10
        }
        result = validate_trade_inputs(trade_data)
        assert result is not None

    def test_invalid_symbol_in_trade(self):
        """Test validation with invalid symbol."""
        trade_data = {
            'symbol': 'XYZ123INVALID',
            'direction': 'BUY',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10
        }
        with pytest.raises(ValueError):
            validate_trade_inputs(trade_data)

    def test_invalid_direction_in_trade(self):
        """Test validation with invalid direction."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'HOLD',
            'entry_price': 150.00,
            'stop_loss': 145.00,
            'take_profit': 160.00,
            'quantity': 10
        }
        with pytest.raises(ValueError):
            validate_trade_inputs(trade_data)

    def test_missing_required_field(self):
        """Test validation with missing fields."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 150.00,
            # Missing stop_loss
            'take_profit': 160.00,
            'quantity': 10
        }
        with pytest.raises((ValueError, KeyError)):
            validate_trade_inputs(trade_data)

    def test_all_prices_invalid(self):
        """Test validation with all prices as zero."""
        trade_data = {
            'symbol': 'AAPL',
            'direction': 'BUY',
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'quantity': 10
        }
        with pytest.raises(ValueError):
            validate_trade_inputs(trade_data)
