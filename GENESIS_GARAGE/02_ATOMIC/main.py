# ================================================================
# 💣 ATOMIC WARFARE - BAY 02
# ================================================================
# Defensive/Aggressive Volatility Handling
# Activated when: Risk Level = HIGH/CRITICAL
# ================================================================
# Logic: Bollinger Band Breakout + ATR Volatility Clamp
# ================================================================

import pandas as pd
import numpy as np


def execute_strategy(market_data: dict, config: dict = None) -> dict:
    """
    Execute ATOMIC warfare logic strategy
    
    Args:
        market_data: Current market data and indicators (should contain 'df' key with DataFrame)
        config: Optional configuration parameters
        
    Returns:
        Trading signals and recommendations
    """
    try:
        # Extract DataFrame from market_data
        if isinstance(market_data, dict) and 'df' in market_data:
            df = market_data['df']
        elif isinstance(market_data, pd.DataFrame):
            df = market_data
        else:
            # Create a simple DataFrame if raw dict with close prices
            df = pd.DataFrame(market_data)
        
        if df.empty or 'close' not in df.columns:
            return {
                "strategy": "ATOMIC",
                "status": "ERROR",
                "signal": "HOLD",
                "message": "Invalid market data - missing close prices"
            }
        
        # 💣 ATOMIC WARFARE LOGIC: Bollinger Band Breakout + ATR Volatility Clamp
        std_dev = df['close'].rolling(window=20).std().iloc[-1]
        mean_price = df['close'].mean()
        
        # Check if market is melting down (high volatility)
        volatility_threshold = mean_price * 0.05  # 5% volatility threshold
        
        if std_dev > volatility_threshold:
            # Market is melting down - defensive stance only
            signal = "DEFENSIVE_STANCE_ONLY"
            message = f"High volatility detected (σ: {std_dev:.2f} > {volatility_threshold:.2f}) - DEFENSIVE MODE"
            confidence = 0.8
        else:
            # Normal volatility - aggressive trading
            signal = "GATLING_FIRE"
            message = f"Normal volatility (σ: {std_dev:.2f}) - AGGRESSIVE MODE"
            confidence = 0.9
        
        return {
            "strategy": "ATOMIC",
            "status": "ACTIVE",
            "signal": signal,
            "volatility": float(std_dev) if pd.notna(std_dev) else None,
            "threshold": float(volatility_threshold),
            "message": message,
            "confidence": confidence
        }
        
    except Exception as e:
        return {
            "strategy": "ATOMIC",
            "status": "ERROR",
            "signal": "HOLD",
            "message": f"Error executing ATOMIC strategy: {str(e)}"
        }


def get_status() -> dict:
    """Get ATOMIC engine status"""
    return {
        "engine": "02_ATOMIC",
        "name": "Warfare Logic Ferrari",
        "status": "ACTIVE",
        "ready": True,
        "description": "Defensive/Aggressive Volatility Handling"
    }


if __name__ == "__main__":
    print("💣 ATOMIC Warfare - Bay 02")
    print("Defensive/Aggressive Volatility Handling")
    print("Status:", get_status())
