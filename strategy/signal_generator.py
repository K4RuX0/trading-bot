import pandas as pd
import numpy as np

class SmartSignalGenerator:
    def __init__(self, fast_window=10, slow_window=30):
        if fast_window >= slow_window:
            raise ValueError("fast_window deve ser menor que slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window

    def on_candle(self, df: pd.DataFrame):
        if len(df) < self.slow_window:
            return None
        fast_ma = df['close'].rolling(self.fast_window).mean().values
        slow_ma = df['close'].rolling(self.slow_window).mean().values
        fast_last, slow_last = fast_ma[-1], slow_ma[-1]
        if np.isnan(fast_last) or np.isnan(slow_last):
            return None
        if fast_last > slow_last:
            return "BUY"
        elif fast_last < slow_last:
            return "SELL"
        return None

    def generate_series(self, df: pd.DataFrame):
        if len(df) < self.slow_window:
            return pd.Series([None]*len(df), index=df.index)
        fast_ma = df['close'].rolling(self.fast_window).mean()
        slow_ma = df['close'].rolling(self.slow_window).mean()
        signals = pd.Series(index=df.index, dtype=object)
        signals[fast_ma > slow_ma] = "BUY"
        signals[fast_ma < slow_ma] = "SELL"
        signals[fast_ma == slow_ma] = None
        return signals
