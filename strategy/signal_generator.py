# strategy/signal_generator.py
import pandas as pd

class SignalGenerator:
    def __init__(self, fast_window=10, slow_window=30):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def on_candle(self, df: pd.DataFrame):
        if len(df) < self.slow_window:
            return None
        fast_ma = df['close'].rolling(self.fast_window).mean()
        slow_ma = df['close'].rolling(self.slow_window).mean()
        if fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            return "BUY"
        elif fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return "SELL"
        return None
