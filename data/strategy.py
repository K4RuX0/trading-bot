"""
Signal generator: Moving Average Crossover (fast, slow) with optional RSI and MACD filters.
Interface:
  - on_candle(history_df) -> "BUY" | "SELL" | "HOLD"
Strategy is agnostic to broker/execution.
"""
import pandas as pd
import numpy as np
import pandas_ta as ta

class SignalGenerator:
    def __init__(self, fast_window: int = 20, slow_window: int = 50,
                 rsi_length: int = 14, oversold: int = 30, overbought: int = 70,
                 atr_length: int = 14):
        assert fast_window < slow_window, "fast_window should be < slow_window"
        self.fast = fast_window
        self.slow = slow_window
        self.rsi_length = rsi_length
        self.oversold = oversold
        self.overbought = overbought
        self.atr_length = atr_length
        self._last_signal = "HOLD"

    # -----------------------------
    def _sma(self, series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window=window, min_periods=1).mean()

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores necessários: SMA rápido/lento, RSI, ATR e MACD
        """
        df = df.copy()
        df['sma_fast'] = self._sma(df['close'], self.fast)
        df['sma_slow'] = self._sma(df['close'], self.slow)
        df['sma_diff'] = df['sma_fast'] - df['sma_slow']

        # RSI
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_length).fillna(50)

        # ATR
        df['atr'] = self.calculate_atr(df)

        # MACD (opcional)
        macd = ta.macd(df['close'], fast=self.fast, slow=self.slow, signal=9)
        if macd is not None:
            df['macd'] = macd[f"MACD_{self.fast}_{self.slow}_9"]
            df['macd_signal'] = macd[f"MACDs_{self.fast}_{self.slow}_9"]
        else:
            df['macd'] = 0
            df['macd_signal'] = 0

        return df

    # -----------------------------
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close']

        df_tmp = df.copy()
        df_tmp['H-L'] = high - low
        df_tmp['H-PC'] = abs(high - close.shift(1))
        df_tmp['L-PC'] = abs(low - close.shift(1))
        true_range = df_tmp[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = true_range.rolling(window=self.atr_length).mean()
        return atr.fillna(0)

    # -----------------------------
    def on_candle(self, history_df: pd.DataFrame) -> str:
        """
        Recebe o histórico até a vela atual (inclusive) e retorna:
        'BUY', 'SELL' ou 'HOLD'
        """
        if len(history_df) < 2:
            return "HOLD"

        df = self.compute_indicators(history_df)
        prev = df.iloc[-2]
        cur = df.iloc[-1]

        # SMA Crossover
        cross_up = prev['sma_diff'] <= 0 and cur['sma_diff'] > 0
        cross_down = prev['sma_diff'] >= 0 and cur['sma_diff'] < 0

        # RSI Filter
        oversold_signal = cur['rsi'] < self.oversold
        overbought_signal = cur['rsi'] > self.overbought

        # MACD trend filter
        macd_bull = cur['macd'] > cur['macd_signal']
        macd_bear = cur['macd'] < cur['macd_signal']

        # Decisão final
        if cross_up and oversold_signal and macd_bull:
            self._last_signal = "BUY"
            return "BUY"
        elif cross_down and overbought_signal and macd_bear:
            self._last_signal = "SELL"
            return "SELL"
        else:
            return "HOLD"
