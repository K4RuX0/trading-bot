import pandas as pd
import numpy as np

class SmartSignalGenerator:
    def __init__(self, fast_window=10, slow_window=30):
        if fast_window >= slow_window:
            raise ValueError("fast_window deve ser menor que slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window

    def on_candle(self, df: pd.DataFrame):
        if df is None or len(df) < self.slow_window:
            return None
        close_prices = df['close'].values.astype(float)
        fast_ma = pd.Series(close_prices).rolling(self.fast_window).mean().values
        slow_ma = pd.Series(close_prices).rolling(self.slow_window).mean().values
        fast_last = fast_ma[-1]
        slow_last = slow_ma[-1]
        if np.isnan(fast_last) or np.isnan(slow_last):
            return None
        if fast_last > slow_last:
            return "BUY"
        elif fast_last < slow_last:
            return "SELL"
        else:
            return None
