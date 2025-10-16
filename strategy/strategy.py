import pandas as pd

class SignalGenerator:
    def __init__(self, fast_window=10, slow_window=30):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def on_candle(self, df: pd.DataFrame):
        if len(df) < self.slow_window:
            return None
        df['fast_ma'] = df['close'].rolling(self.fast_window).mean()
        df['slow_ma'] = df['close'].rolling(self.slow_window).mean()
        if df['fast_ma'].iloc[-1] > df['slow_ma'].iloc[-1]:
            return "BUY"
        elif df['fast_ma'].iloc[-1] < df['slow_ma'].iloc[-1]:
            return "SELL"
        else:
            return None
