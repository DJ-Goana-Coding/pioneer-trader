import pandas as pd
import pandas_ta as ta

class StrategyEngine:
    def __init__(self):
        pass

    def calculate_indicators(self, df: pd.DataFrame):
        # Example: RSI and SMA
        df.ta.rsi(length=14, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        return df

    def check_signal(self, df: pd.DataFrame):
        # Simple Crossover Strategy Example
        # Ensure we have enough data
        if len(df) < 50:
            return "NEUTRAL"
            
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # Golden Cross (SMA 20 crosses above SMA 50)
        if prev_row['SMA_20'] <= prev_row['SMA_50'] and last_row['SMA_20'] > last_row['SMA_50']:
            return "BUY"
            
        # Death Cross (SMA 20 crosses below SMA 50)
        if prev_row['SMA_20'] >= prev_row['SMA_50'] and last_row['SMA_20'] < last_row['SMA_50']:
            return "SELL"
            
        return "NEUTRAL"
