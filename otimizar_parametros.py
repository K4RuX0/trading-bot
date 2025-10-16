import pandas as pd
import numpy as np
from backtester import executar_backtest

NUM_COMBINATIONS = 50

def gerar_combinacoes(df, num_combinations=NUM_COMBINATIONS):
    rng = np.random.default_rng()
    combs = []
    for _ in range(num_combinations):
        fast = int(rng.integers(5, 30))
        slow = int(rng.integers(max(fast+1,30),60))
        combs.append({"df":df, "fast_window":fast, "slow_window":slow})
    return combs

def otimizar_parametros_continuo(df, num_combinations=NUM_COMBINATIONS):
    combs = gerar_combinacoes(df, num_combinations)
    results = [executar_backtest(c['df'], c['fast_window'], c['slow_window']) for c in combs]
    best = max(results, key=lambda x: x['total_return'])
    return best
