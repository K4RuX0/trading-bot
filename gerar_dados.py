import pandas as pd
import numpy as np

# Configurações
inicio = "2024-01-01 00:00:00"
fim = "2024-01-31 23:00:00"
intervalo = "1H"
preco_inicial = 100.0
volatilidade = 0.02  # Aumentei a volatilidade para 2%
drift = 0.0005  # Reduzi a tendência de alta para 0.05% por hora
crash_time = "2024-01-15 12:00:00"
crash_amplitude = 0.2  # Aumentei a queda para 20%

# Gerar o dataframe
datas = pd.date_range(start=inicio, end=fim, freq=intervalo)
df = pd.DataFrame(datas, columns=["timestamp"])

# Gerar os preços
df["open"] = preco_inicial + np.cumsum(np.random.normal(drift, volatilidade, len(df)))
df["high"] = df["open"] + np.random.uniform(0, volatilidade * 3, len(df))
df["low"] = df["open"] - np.random.uniform(0, volatilidade * 3, len(df))
df["close"] = (df["open"] + df["high"] + df["low"]) / 3

# Simular o crash
crash_index = df[df["timestamp"] == crash_time].index[0]
df.loc[crash_index:, "open"] *= (1 - crash_amplitude)
df.loc[crash_index:, "high"] *= (1 - crash_amplitude)
df.loc[crash_index:, "low"] *= (1 - crash_amplitude)
df.loc[crash_index:, "close"] *= (1 - crash_amplitude)

# Gerar o volume
df["volume"] = np.random.randint(10, 50, len(df))

# Arredondar os preços
df["open"] = df["open"].round(2)
df["high"] = df["high"].round(2)
df["low"] = df["low"].round(2)
df["close"] = df["close"].round(2)

# Salvar o dataframe em um arquivo CSV
df.to_csv("data/sample_ohlcv.csv", index=False)

print("Dados gerados e salvos em data/sample_ohlcv.csv")