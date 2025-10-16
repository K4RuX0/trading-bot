from .signal_generator import SignalGenerator
import pandas as pd

class SmartSignalGenerator(SignalGenerator):
    """Extensão para sinais inteligentes e backtests avançados."""
    def generate_series(self, df):
        if len(df) < self.slow_window:
            return pd.Series([None]*len(df), index=df.index)
        fast_ma = df['close'].rolling(self.fast_window).mean()
        slow_ma = df['close'].rolling(self.slow_window).mean()
        signals = pd.Series(index=df.index, dtype=object)
        signals[fast_ma > slow_ma] = "BUY"
        signals[fast_ma < slow_ma] = "SELL"
        signals[fast_ma == slow_ma] = None
        return signals
