import os

# ----------------- API KEYS ----------------- #
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "Ranyellson@gmail.com")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "-+Ran1708")

# ----------------- SYMBOLOS ----------------- #
SYMBOLS_BINANCE = ["BTCUSDT", "ETHUSDT"]
SYMBOLS_MT5 = ["EURUSD", "USDJPY"]

# ----------------- INTERVALOS ----------------- #
INTERVAL = "1h"
SLEEP_INTERVAL = 3600

# ----------------- CAPITAL E RISCO ----------------- #
INITIAL_CASH = 10000
LOT_MIN = 0.001
MAX_RISK = 0.03
TP_MULTIPLIER = 1.5
ATR_PERIOD = 14

# ----------------- OTIMIZAÇÃO ----------------- #
NUM_COMBINATIONS = 50
