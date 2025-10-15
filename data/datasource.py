"""
DataSource simples: carrega CSV OHLCV e expõe interface mínima.
Pode ser estendido para providers (exchange APIs, websocket, database).
"""

import pandas as pd
from typing import Optional

class CSVDataSource:
    def __init__(self, filepath: str, timestamp_col: str = "timestamp"):
        self.filepath = filepath
        self.timestamp_col = timestamp_col

    def load_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath)
        # Normalizar nomes:
        expected = ['timestamp','open','high','low','close','volume']
        # Allow timestamp column named differently (e.g., time)
        if self.timestamp_col not in df.columns and 'time' in df.columns:
            self.timestamp_col = 'time'
        # Ensure required cols exist
        missing = [c for c in expected if c not in df.columns]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")
        df = df[expected].copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
