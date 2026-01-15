import pandas_ta as ta
import pandas as pd

class StrategyLogic:
    def p25_momentum(self, df: pd.DataFrame) -> str:
        # P25: RSI < 30 (Buy) / RSI > 70 (Sell)
        if df.empty or len(df) < 14: return "HOLD"
        rsi = df.ta.rsi(length=14).iloc[-1]
        if rsi < 30: return "BUY"
        if rsi > 70: return "SELL"
        return "HOLD"

    def golden_cross(self, df: pd.DataFrame) -> str:
        # Golden Cross: SMA50 > SMA200
        if df.empty or len(df) < 200: return "HOLD"
        sma50 = df.ta.sma(length=50)
        sma200 = df.ta.sma(length=200)
        if sma50.iloc[-1] > sma200.iloc[-1] and sma50.iloc[-2] <= sma200.iloc[-2]:
            return "BUY"
        return "HOLD"