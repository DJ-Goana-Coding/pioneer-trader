# ================================================================
# 👑 FUSION PRIME - BAY 04
# ================================================================
# T.I.A. Command Logic
# Activated when: T.I.A. Override / Special Conditions
# ================================================================
# Logic: Golden Cross (SMA 50/200) + T.I.A. Confidence Check
# This engine communicates with backend/services/tia_agent.py
# ================================================================

import pandas as pd


def execute_strategy(market_data: dict, config: dict = None) -> dict:
    """
    Execute FUSION (T.I.A. + Scavenged Math) strategy
    
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
                "strategy": "FUSION",
                "status": "ERROR",
                "signal": "HOLD",
                "message": "Invalid market data - missing close prices"
            }
        
        # 👑 FUSION PRIME LOGIC: Golden Cross (SMA 50/200) + T.I.A. Confidence Check
        # Calculate SMAs if we have enough data
        if len(df) >= 200:
            sma50 = df['close'].rolling(window=50).mean().iloc[-1]
            sma200 = df['close'].rolling(window=200).mean().iloc[-1]
            
            # Check for golden cross or death cross
            if sma50 > sma200:
                signal = "FUSION_ACTIVE_AWAITING_TIA_CONFIRMATION"
                message = f"Golden Cross detected (SMA50: {sma50:.2f} > SMA200: {sma200:.2f}) - Awaiting T.I.A. confirmation"
                confidence = 0.85
            else:
                signal = "FUSION_STANDBY"
                message = f"Death Cross condition (SMA50: {sma50:.2f} < SMA200: {sma200:.2f}) - Fusion on standby"
                confidence = 0.5
            
            return {
                "strategy": "FUSION",
                "status": "ACTIVE",
                "signal": signal,
                "sma50": float(sma50) if pd.notna(sma50) else None,
                "sma200": float(sma200) if pd.notna(sma200) else None,
                "message": message,
                "confidence": confidence,
                "tia_integration": True
            }
        else:
            # Not enough data for golden cross
            return {
                "strategy": "FUSION",
                "status": "ACTIVE",
                "signal": "FUSION_ACTIVE_AWAITING_TIA_CONFIRMATION",
                "message": f"Insufficient data for Golden Cross ({len(df)}/200 bars) - Awaiting T.I.A. confirmation",
                "confidence": 0.6,
                "tia_integration": True
            }
        
    except Exception as e:
        return {
            "strategy": "FUSION",
            "status": "ERROR",
            "signal": "HOLD",
            "message": f"Error executing FUSION strategy: {str(e)}"
        }


def get_status() -> dict:
    """Get FUSION engine status"""
    return {
        "engine": "04_FUSION",
        "name": "T.I.A. Prime Ferrari",
        "status": "ACTIVE",
        "ready": True,
        "description": "Golden Cross + T.I.A. Confidence Integration"
    }


if __name__ == "__main__":
    print("👑 FUSION Prime - Bay 04")
    print("T.I.A. Command Logic")
    print("Status:", get_status())
