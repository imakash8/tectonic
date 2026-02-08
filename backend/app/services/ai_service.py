"""
AI/LLM service for trade validation and market analysis
"""

import logging
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered trading intelligence"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
    
    async def validate_trade(
        self,
        symbol: str,
        direction: str,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gate 9: AI qualitative validation"""
        
        prompt = f"""
        Analyze this potential trade and provide validation:
        
        TRADE DETAILS:
        - Symbol: {symbol}
        - Direction: {direction}
        - Current Price: ${market_data.get('price', 0):.2f}
        - Entry Price: ${market_data.get('entry_price', 0):.2f}
        - Stop Loss: ${market_data.get('stop_loss', 0):.2f}
        - Take Profit: ${market_data.get('take_profit', 0):.2f}
        
        MARKET CONTEXT:
        - Volume: {market_data.get('volume', 0):,.0f}
        - Change: {market_data.get('change_percent', 0):.2f}%
        - High (24h): ${market_data.get('high', 0):.2f}
        - Low (24h): ${market_data.get('low', 0):.2f}
        
        Provide:
        1. Confidence Score (0.0-1.0)
        2. Key Risks
        3. Technical Validation
        4. Recommendation (APPROVE/REJECT)
        
        Respond in JSON format:
        {{
            "confidence": 0.0,
            "risks": [],
            "technical_analysis": "",
            "recommendation": "APPROVE",
            "reasoning": ""
        }}
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {response_text}")
                return {
                    "confidence": 0.3,
                    "risks": ["Unable to parse AI response"],
                    "technical_analysis": "Error in analysis",
                    "recommendation": "REJECT",
                    "reasoning": "AI service error"
                }
                
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            return {
                "confidence": 0.0,
                "risks": [str(e)],
                "technical_analysis": "Service unavailable",
                "recommendation": "REJECT",
                "reasoning": "AI service unavailable"
            }
    
    async def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall market conditions"""
        
        prompt = f"""
        Analyze current market conditions:
        
        MARKET DATA:
        {json.dumps(market_data, indent=2, default=str)}
        
        Provide:
        1. Market Regime (Trending/Ranging/Volatile)
        2. Risk Level (Low/Medium/High)
        3. Trading Bias (Bullish/Neutral/Bearish)
        4. Key Support/Resistance Levels
        
        Respond in JSON format.
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                return {"analysis": response_text}
                
        except Exception as e:
            logger.error(f"Market analysis error: {str(e)}")
            return {"error": str(e)}
    
    async def generate_strategy_recommendation(
        self,
        portfolio_stats: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate strategy recommendations based on portfolio and market conditions"""
        
        prompt = f"""
        Based on portfolio statistics and market conditions, provide trading recommendations:
        
        PORTFOLIO:
        {json.dumps(portfolio_stats, indent=2, default=str)}
        
        MARKET CONDITIONS:
        {json.dumps(market_conditions, indent=2, default=str)}
        
        Provide strategic recommendations for the next trading period.
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "recommendation": message.content[0].text
            }
            
        except Exception as e:
            logger.error(f"Strategy recommendation error: {str(e)}")
            return {"error": str(e)}
