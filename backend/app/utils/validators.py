"""
9-Gate validation system for trades
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ValidationGates:
    """Nine-gate validation system for trading signals"""
    
    # Configuration
    MAX_QUOTE_AGE_SECONDS = 60  # Allow up to 1 minute old quotes
    MAX_PRICE_DEVIATION_FROM_ENTRY = 0.03  # 3%
    MAX_PRICE_DEVIATION_FROM_CLOSE = 0.30  # 30%
    MIN_CONFIDENCE = 0.3
    
    def __init__(self):
        self.gates_status = {}
    
    def validate_all_gates(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Run all 9 validation gates"""
        
        gates_results = {
            "gate_1": self.gate_1_quote_freshness(data),
            "gate_2": self.gate_2_price_deviation(data),
            "gate_3": self.gate_3_liquidity_check(data),
            "gate_4": self.gate_4_volatility_regime(data),
            "gate_5": self.gate_5_market_hours(data),
            "gate_6": self.gate_6_risk_reward_ratio(data),
            "gate_7": self.gate_7_portfolio_exposure(data),
            "gate_8": self.gate_8_order_flow_pressure(data),
            "gate_9": self.gate_9_ai_confidence(data),
        }
        
        # Check if all gates passed
        all_passed = all(gate["passed"] for gate in gates_results.values())
        
        return all_passed, gates_results
    
    def gate_1_quote_freshness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 1: Check if quote is fresh (not older than 30 seconds)"""
        quote_timestamp = data.get("quote_timestamp")
        now = datetime.utcnow()
        
        if not quote_timestamp:
            return {"passed": False, "reason": "No quote timestamp", "gate": 1}
        
        age = (now - quote_timestamp).total_seconds()
        
        if age > self.MAX_QUOTE_AGE_SECONDS:
            return {"passed": False, "reason": f"Quote too old: {age}s", "gate": 1}
        
        return {"passed": True, "reason": f"Quote fresh: {age}s old", "gate": 1}
    
    def gate_2_price_deviation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 2: Check price deviation from proposed entry and previous close"""
        current_price = data.get("current_price", 0)
        entry_price = data.get("entry_price", 0)
        prev_close = data.get("prev_close", 0)
        
        if not all([current_price, entry_price, prev_close]):
            return {"passed": False, "reason": "Missing price data", "gate": 2}
        
        # Check deviation from entry price
        entry_deviation = abs(current_price - entry_price) / entry_price
        if entry_deviation > self.MAX_PRICE_DEVIATION_FROM_ENTRY:
            return {"passed": False, "reason": f"Entry deviation {entry_deviation:.2%} too high", "gate": 2}
        
        # Check deviation from previous close
        close_deviation = abs(current_price - prev_close) / prev_close
        if close_deviation > self.MAX_PRICE_DEVIATION_FROM_CLOSE:
            return {"passed": False, "reason": f"Close deviation {close_deviation:.2%} too high", "gate": 2}
        
        return {"passed": True, "reason": "Price deviation within limits", "gate": 2}
    
    def gate_3_liquidity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 3: Check if symbol has sufficient liquidity"""
        volume = data.get("volume", 0)
        min_volume = 100000  # Minimum daily volume
        
        if volume < min_volume:
            return {"passed": False, "reason": f"Low volume: {volume}", "gate": 3}
        
        return {"passed": True, "reason": f"Sufficient liquidity: {volume}", "gate": 3}
    
    def gate_4_volatility_regime(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 4: Check volatility regime"""
        volatility = data.get("volatility", 0)
        vix = data.get("vix", 20)
        
        # Very high volatility/VIX signals uncertain regime
        if vix > 40:
            return {"passed": False, "reason": f"VIX too high: {vix}", "gate": 4}
        
        return {"passed": True, "reason": f"Volatility acceptable: VIX {vix}", "gate": 4}
    
    def gate_5_market_hours(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 5: Check if market is open"""
        market_open = data.get("market_open", True)
        
        if not market_open:
            return {"passed": False, "reason": "Market closed", "gate": 5}
        
        return {"passed": True, "reason": "Market open", "gate": 5}
    
    def gate_6_risk_reward_ratio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 6: Check risk-reward ratio"""
        entry = data.get("entry_price", 0)
        stop = data.get("stop_loss", 0)
        target = data.get("take_profit", 0)
        
        if not all([entry, stop, target]):
            return {"passed": False, "reason": "Missing price levels", "gate": 6}
        
        risk = abs(entry - stop)
        reward = abs(target - entry)
        
        if risk == 0:
            return {"passed": False, "reason": "Invalid risk calculation", "gate": 6}
        
        ratio = reward / risk
        min_ratio = 1.5 if data.get("timeframe") == "day" else 2.0
        
        if ratio < min_ratio:
            return {"passed": False, "reason": f"R:R {ratio:.2f} below minimum {min_ratio}", "gate": 6}
        
        return {"passed": True, "reason": f"R:R ratio {ratio:.2f} acceptable", "gate": 6}
    
    def gate_7_portfolio_exposure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 7: Check portfolio exposure/diversification"""
        current_exposure = data.get("current_exposure", 0.0)  # % of portfolio
        trade_size = data.get("trade_size", 0.0)  # % of portfolio
        max_exposure = 0.5  # 50% max in single position
        
        total_exposure = current_exposure + trade_size
        
        if total_exposure > max_exposure:
            return {"passed": False, "reason": f"Total exposure {total_exposure:.1%} exceeds limit", "gate": 7}
        
        return {"passed": True, "reason": f"Exposure within limits: {total_exposure:.1%}", "gate": 7}
    
    def gate_8_order_flow_pressure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 8: Check order flow pressure (simplified)"""
        buy_pressure = data.get("buy_volume", 0)
        sell_pressure = data.get("sell_volume", 0)
        
        if buy_pressure + sell_pressure == 0:
            return {"passed": True, "reason": "No order flow data", "gate": 8}
        
        buy_ratio = buy_pressure / (buy_pressure + sell_pressure)
        
        # Check if direction aligns with order flow
        direction = data.get("direction", "")
        if direction == "BUY" and buy_ratio < 0.45:
            return {"passed": False, "reason": f"Sell pressure dominant: {1-buy_ratio:.1%}", "gate": 8}
        
        if direction == "SELL" and buy_ratio > 0.55:
            return {"passed": False, "reason": f"Buy pressure dominant: {buy_ratio:.1%}", "gate": 8}
        
        return {"passed": True, "reason": "Order flow pressure acceptable", "gate": 8}
    
    def gate_9_ai_confidence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gate 9: Check AI confidence score"""
        confidence = data.get("ai_confidence", 0.0)
        
        if confidence < self.MIN_CONFIDENCE:
            return {"passed": False, "reason": f"AI confidence {confidence:.1%} below threshold", "gate": 9}
        
        return {"passed": True, "reason": f"AI confidence: {confidence:.1%}", "gate": 9}
