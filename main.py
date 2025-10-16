# main.py
import pandas as pd
import numpy as np
from utils.logger import get_logger
from helpers.helpers import calculate_atr                   # helpers/helpers.py
from risk_manager.risk_manager import RiskManager           # risk_manager/risk_manager.py
from strategy.signal_generator import SignalGenerator       # strategy/signal_generator.py
from execution.broker_adapter import BrokerAdapter          # execution/broker_adapter.py
from otimizar_parametros import otimizar_parametros_continuo
from config import *

from binance import ThreadedWebsocketManager
import threading
import time

logger = get_logger("AutoTraderPro_HF")

# Inicializa brokers
broker = BrokerAdapter(BINANCE_API_KEY, BINANCE_API_SECRET)
positions = {}  # Guarda posições abertas Binance+MT5

# ---------------- FUNÇÃO DE TRADING ---------------- #
def process_symbol(symbol, mt5_symbol, best_params, test_mode=True):
    try:
        df = broker.get_ohlcv(symbol, INTERVAL, limit=200)
        price = df['close'].iloc[-1]
        atr = calculate_atr(df, ATR_PERIOD)

        signal_gen = SignalGenerator(
            fast_window=int(best_params['fast_window']),
            slow_window=int(best_params['slow_window'])
        )
        signal = signal_gen.on_candle(df)

        rm = RiskManager(capital=broker.get_balance("USDT"), risk_per_trade=best_params.get("risk_per_trade", MAX_RISK))
        quantity = max(rm.position_size(price, atr), LOT_MIN)

        # Ajuste dinâmico de risco
        risk_factor = 1.0
        if "max_drawdown" in best_params and best_params["max_drawdown"] < -0.1:
            risk_factor = 0.5
        quantity *= risk_factor

        if symbol not in positions:
            if signal == "BUY":
                broker.execute_binance_order(symbol, "BUY", quantity, test_mode)
                broker.execute_mt5_order(mt5_symbol, "SELL", quantity, test_mode)
                positions[symbol] = {"side":"BUY","entry":price,"stop_loss":price-atr,"take_profit":price+atr*TP_MULTIPLIER,"quantity":quantity}
            elif signal == "SELL":
                broker.execute_binance_order(symbol, "SELL", quantity, test_mode)
                broker.execute_mt5_order(mt5_symbol, "BUY", quantity, test_mode)
                positions[symbol] = {"side":"SELL","entry":price,"stop_loss":price+atr,"take_profit":price-atr*TP_MULTIPLIER,"quantity":quantity}

    except Exception as e:
        logger.error(f"[{symbol}] Erro no processamento: {e}")

# ---------------- WEBSOCKET CALLBACK ---------------- #
def handle_socket_message(msg, best_params):
    if msg['e'] != 'error':
        symbol = msg['s']
        mt5_symbol = SYMBOLS_MT5[SYMBOLS_BINANCE.index(symbol)]
        threading.Thread(target=process_symbol, args=(symbol, mt5_symbol, best_params, True)).start()

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    while True:
        try:
            # Carrega dados para otimização inicial
            df = pd.read_csv("data/sample_ohlcv.csv")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)

            best_params = otimizar_parametros_continuo(df, num_combinations=NUM_COMBINATIONS)
            logger.info(f"[MAIN] Melhor parâmetro inicial: {best_params}")

            # Inicializa WebSocket Binance
            twm = ThreadedWebsocketManager(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
            twm.start()

            for symbol in SYMBOLS_BINANCE:
                twm.start_kline_socket(callback=lambda msg, bp=best_params: handle_socket_message(msg, bp),
                                       symbol=symbol.lower(), interval=INTERVAL)

            logger.info("WebSockets iniciados. Bot HFT 24/7 rodando...")
            while True:
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Encerrando AutoTraderPro_HF")
            twm.stop()
            break
        except Exception as e:
            logger.error(f"Erro crítico no loop principal: {e}")
            time.sleep(10)
