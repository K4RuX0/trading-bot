import pandas as pd
import numpy as np

def calculate_atr(df, period=14):
    high, low, close = df['high'], df['low'], df['close']
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

def pct(value, total):
    return (value / total) * 100 if total != 0 else 0

def round_price(price, decimals=2):
    return round(price, decimals)

def format_float(value, decimals=2):
    return f"{value:.{decimals}f}"

def safe_divide(a, b):
    return a / b if b != 0 else 0
