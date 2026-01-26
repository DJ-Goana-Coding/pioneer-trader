# ================================================================
# ⏱️ CLOCKWORK - BAY 03
# ================================================================
# 60-Second Cycle Scalping
# Activated when: Risk Level = MEDIUM
# ================================================================
# Logic: 1-minute EMA Crossover (Fast Scalp)
# ================================================================

import pandas as pd


def execute_strategy(market_data: dict, config: dict = None) -> dict:
    """
    Execute CLOCKWORK cycle logic strategy
    
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
                "strategy": "CLOCKWORK",
                "status": "ERROR",
                "signal": "HOLD",
                "message": "Invalid market data - missing close prices"
            }
        
        # ⏱️ CLOCKWORK LOGIC: 1-minute EMA Crossover (Fast Scalp)
        ema9 = df['close'].ewm(span=9).mean().iloc[-1]
        ema21 = df['close'].ewm(span=21).mean().iloc[-1]
        
        if ema9 > ema21:
            signal = "BUY"
            message = f"EMA9 ({ema9:.2f}) > EMA21 ({ema21:.2f}) - Bullish crossover"
        else:
            signal = "SELL"
            message = f"EMA9 ({ema9:.2f}) < EMA21 ({ema21:.2f}) - Bearish crossover"
        
        # Calculate crossover strength
        crossover_strength = abs(ema9 - ema21) / ema21 * 100
        confidence = min(0.5 + (crossover_strength * 2), 0.95)
        
        return {
            "strategy": "CLOCKWORK",
            "status": "ACTIVE",
            "signal": signal,
            "ema9": float(ema9) if pd.notna(ema9) else None,
            "ema21": float(ema21) if pd.notna(ema21) else None,
            "crossover_strength": float(crossover_strength),
            "message": message,
            "confidence": confidence
        }
        
    except Exception as e:
        return {
            "strategy": "CLOCKWORK",
            "status": "ERROR",
            "signal": "HOLD",
            "message": f"Error executing CLOCKWORK strategy: {str(e)}"
        }


def get_status() -> dict:
    """Get CLOCKWORK engine status"""
    return {
        "engine": "03_CLOCKWORK",
        "name": "Cycle Logic Ferrari",
        "status": "ACTIVE",
        "ready": True,
        "description": "60-Second Cycle Scalping with EMA Crossover"
    }


if __name__ == "__main__":
    print("⏱️ CLOCKWORK - Bay 03")
    print("60-Second Cycle Scalping Strategy")
    print("Status:", get_status())
