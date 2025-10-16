import pandas as pd
import numpy as np
from strategy.signal_generator import SmartSignalGenerator

def executar_backtest(df, fast_window, slow_window, initial_cash=10000):
    signal_gen = SmartSignalGenerator(fast_window, slow_window)
    equity = [initial_cash]
    positions = []
    for i in range(len(df)):
        price = df['close'].iloc[i]
        signal = signal_gen.on_candle(df.iloc[:i+1])
        if signal == "BUY" and not positions:
            positions.append({'entry': price, 'size':1})
        elif signal == "SELL" and positions:
            positions.pop()
        total = initial_cash + sum((price - pos["entry"])*pos["size"] for pos in positions)
        equity.append(total)
    total_return = (equity[-1]-initial_cash)/initial_cash
    max_dd = np.min(np.array(equity)/np.maximum.accumulate(equity)-1)
    return {"fast_window": fast_window, "slow_window": slow_window, "total_return": total_return, "max_drawdown": max_dd}
