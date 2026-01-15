import pandas_ta as ta
import pandas as pd
class StrategyLogic:
    def p25_momentum(self, df: pd.DataFrame) -> str:
        if df.empty or len(df) < 14: return "HOLD"
        rsi = df.ta.rsi(length=14).iloc[-1]
        if rsi < 30: return "BUY"
        if rsi > 70: return "SELL"
        return "HOLD"
    def golden_cross(self, df: pd.DataFrame) -> str:
        if df.empty or len(df) < 200: return "HOLD"
        s50 = df.ta.sma(length=50); s200 = df.ta.sma(length=200)
        if s50.iloc[-1] > s200.iloc[-1] and s50.iloc[-2] <= s200.iloc[-2]: return "BUY"
        return "HOLD"
