import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, fast_window, slow_window):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def on_candle(self, df: pd.DataFrame):
        # Calcula as médias móveis com base nos parâmetros atuais
        fast_ma = df['close'].rolling(window=self.fast_window).mean()
        slow_ma = df['close'].rolling(window=self.slow_window).mean()
        atr = self.calculate_atr(df)

        if fast_ma.iloc[-1] > slow_ma.iloc[-1] and fast_ma.iloc[-2] <= slow_ma.iloc[-2]:
            return "BUY"
        elif fast_ma.iloc[-1] < slow_ma.iloc[-1] and fast_ma.iloc[-2] >= slow_ma.iloc[-2]:
            return "SELL"
        return "HOLD"

    def calculate_atr(self, df):
        """Calculates the Average True Range (ATR)"""
        high = df['high']
        low = df['low']
        close = df['close']

        # Use .loc to avoid SettingWithCopyWarning
        df = df.copy()
        df.loc[:, 'H-L'] = high - low
        df.loc[:, 'H-PC'] = abs(high - close.shift(1))
        df.loc[:, 'L-PC'] = abs(low - close.shift(1))

        true_range = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = true_range.rolling(window=14).mean()  # 14 is a common period for ATR
        atr = atr.fillna(0)
        return atr