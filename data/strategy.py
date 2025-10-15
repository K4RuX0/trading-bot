"""
Signal generator: Moving Average Crossover (fast, slow).
Interface:
  - on_candle(history_df) -> "BUY" | "SELL" | "HOLD"
Strategy is agnóstica ao broker/execution.
"""
import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, fast_window: int = 20, slow_window: int = 50):
        assert fast_window < slow_window, "fast_window should be < slow_window"
        self.fast = fast_window
        self.slow = slow_window
        self._last_signal = "HOLD"

    def _sma(self, series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window=window, min_periods=1).mean()

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['sma_fast'] = self._sma(df['close'], self.fast)
        df['sma_slow'] = self._sma(df['close'], self.slow)
        df['sma_diff'] = df['sma_fast'] - df['sma_slow']
        return df

    def on_candle(self, history_df: pd.DataFrame) -> str:
        """
        Pass the history up to the current candle (inclusive).
        Returns: "BUY", "SELL", or "HOLD"
        """
        if len(history_df) < 2:
            return "HOLD"
        df = self.compute_indicators(history_df)
        # Use last two points to detect crossover
        if len(df) < 2:
            return "HOLD"
        prev = df.iloc[-2]
        cur = df.iloc[-1]
        # crossing up
        if prev['sma_diff'] <= 0 and cur['sma_diff'] > 0:
            self._last_signal = "BUY"
            return "BUY"
        # crossing down
        if prev['sma_diff'] >= 0 and cur['sma_diff'] < 0:
            self._last_signal = "SELL"
            return "SELL"
        return "HOLD"
