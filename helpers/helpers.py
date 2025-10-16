import pandas as pd

def calculate_atr(df: pd.DataFrame, period=14):
    """Calcula ATR simples"""
    high, low, close = df['high'], df['low'], df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr.iloc[-1]
