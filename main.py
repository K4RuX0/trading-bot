# main.py
import os
import pandas as pd
import numpy as np
import threading
import time
from utils.logger import get_logger
from utils.helpers import calculate_atr
from risk.risk_manager import RiskManager
from signals.strategy import SmartSignalGenerator
from execution.broker_adapter import BrokerAdapter
from otimizar_parametros import otimizar_parametros_continuo
from config import *

from binance import ThreadedWebsocketManager

logger = get_logger("AutoTraderPro_HF")

# ---------------- CONFIGURAÇÃO DE MODO ---------------- #
TEST_MODE = True  # True = apenas simulação / False = operações reais

# ---------------- INICIALIZAÇÃO DE BROKERS ---------------- #
broker = BrokerAdapter(BINANCE_API_KEY, BINANCE_API_SECRET)
positions = {}  # Guarda posições abertas Binance+MT5
positions_lock = threading.Lock()  # Thread-safe

# ---------------- FUNÇÃO DE TRADING ---------------- #
def process_symbol(symbol, mt5_symbol, best_params, test_mode=TEST_MODE):
    try:
        df = broker.get_ohlcv(symbol, INTERVAL, limit=200)
        if df.empty:
            logger.warning(f"[{symbol}] Sem dados OHLCV")
            return

        price = df['close'].iloc[-1]
        atr = calculate_atr(df, ATR_PERIOD)

        signal_gen = SmartSignalGenerator(
            fast_window=int(best_params['fast_window']),
            slow_window=int(best_params['slow_window'])
        )
        signal = signal_gen.on_candle(df)

        rm = RiskManager(
            capital=broker.get_balance("USDT"),
            risk_per_trade=best_params.get("risk_per_trade", MAX_RISK)
        )
        quantity = max(rm.position_size(price, atr), LOT_MIN)

        # Ajuste de risco dinâmico
        risk_factor = 1.0
        if "max_drawdown" in best_params and best_params["max_drawdown"] < -0.1:
            risk_factor = 0.5
        quantity *= risk_factor

        with positions_lock:
            if symbol not in positions:
                if signal == "BUY":
                    broker.execute_binance_order(symbol, "BUY", quantity, test_mode)
                    broker.execute_mt5_order(mt5_symbol, "SELL", quantity, test_mode)
                    positions[symbol] = {"side":"BUY","entry":price,"stop_loss":price-atr,
                                         "take_profit":price+atr*TP_MULTIPLIER,"quantity":quantity}
                elif signal == "SELL":
                    broker.execute_binance_order(symbol, "SELL", quantity, test_mode)
                    broker.execute_mt5_order(mt5_symbol, "BUY", quantity, test_mode)
                    positions[symbol] = {"side":"SELL","entry":price,"stop_loss":price+atr,
                                         "take_profit":price-atr*TP_MULTIPLIER,"quantity":quantity}

    except Exception as e:
        logger.error(f"[{symbol}] Erro no processamento: {e}")

# ---------------- WEBSOCKET CALLBACK ---------------- #
def handle_socket_message(msg, best_params):
    if msg.get('e') != 'error':
        symbol = msg['s']
        if symbol not in SYMBOLS_BINANCE:
            return
        mt5_symbol = SYMBOLS_MT5[SYMBOLS_BINANCE.index(symbol)]
        threading.Thread(target=process_symbol, args=(symbol, mt5_symbol, best_params, TEST_MODE)).start()

# ---------------- FUNÇÃO PRINCIPAL ---------------- #
def main():
    while True:
        try:
            # Carrega dados históricos para otimização inicial
            df = pd.read_csv("data/sample_ohlcv.csv")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)

            best_params = otimizar_parametros_continuo(df, num_combinations=NUM_COMBINATIONS)
            logger.info(f"[MAIN] Melhor parâmetro inicial: {best_params.to_dict()}")

            # Inicializa WebSocket Binance
            twm = ThreadedWebsocketManager(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
            twm.start()

            # Start socket para cada símbolo
            for symbol in SYMBOLS_BINANCE:
                twm.start_kline_socket(
                    callback=lambda msg, bp=best_params: handle_socket_message(msg, bp),
                    symbol=symbol.lower(),
                    interval=INTERVAL
                )

            logger.info("WebSockets iniciados. Bot HFT 24/7 rodando...")
            while True:
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Encerrando AutoTraderPro_HF")
            try:
                twm.stop()
            except:
                pass
            break
        except Exception as e:
            logger.error(f"Erro crítico no loop principal: {e}")
            time.sleep(10)

# ---------------- EXECUÇÃO ---------------- #
if __name__ == "__main__":
    main()
