# main.py
import pandas as pd
import numpy as np
from time import sleep
from utils.logger import get_logger
from helpers import calculate_atr
from risk_manager import RiskManager
from strategy.strategy import SignalGenerator
from broker_adapter import BrokerAdapter
from otimizar_parametros import otimizar_parametros_continuo
from config import *

logger = get_logger("AutoTraderPro_Advanced")

# Inicializa brokers
broker = BrokerAdapter(BINANCE_API_KEY, BINANCE_API_SECRET)
positions = {}  # Guarda posições abertas Binance+MT5

# ---------------- LIVE TRADING AVANÇADO ---------------- #
def run_live_trading(best_params, test_mode=True):
    global positions

    # Saldo simulado ou real
    balance = INITIAL_CASH if test_mode else broker.get_balance("USDT")
    rm = RiskManager(capital=balance, risk_per_trade=best_params.get("risk_per_trade", MAX_RISK))

    for i, symbol in enumerate(SYMBOLS_BINANCE):
        try:
            # Dados OHLC
            df = broker.get_ohlcv(symbol, interval=INTERVAL, limit=200)
            price = df['close'].iloc[-1]
            atr = calculate_atr(df, ATR_PERIOD)

            # Gera sinal
            signal_gen = SignalGenerator(
                fast_window=int(best_params['fast_window']),
                slow_window=int(best_params['slow_window'])
            )
            signal = signal_gen.on_candle(df)

            # Calcula tamanho da posição baseado em risco e ATR
            quantity = max(rm.position_size(price=price, stop_distance=atr), LOT_MIN)

            # Ajuste dinâmico de risco baseado em drawdown
            risk_factor = 1.0
            if "max_drawdown" in best_params and best_params["max_drawdown"] < -0.1:
                risk_factor = 0.5
            quantity *= risk_factor

            # Hedge inverso MT5 + execução Binance
            mt5_symbol = SYMBOLS_MT5[i]
            if symbol not in positions and signal:
                if signal == "BUY":
                    broker.execute_binance_order(symbol, "BUY", quantity, test_mode)
                    broker.execute_mt5_order(mt5_symbol, "SELL", quantity, test_mode)
                    positions[symbol] = {
                        "side": "BUY",
                        "entry": price,
                        "stop_loss": price - atr,
                        "take_profit": price + atr * TP_MULTIPLIER,
                        "quantity": quantity
                    }
                elif signal == "SELL":
                    broker.execute_binance_order(symbol, "SELL", quantity, test_mode)
                    broker.execute_mt5_order(mt5_symbol, "BUY", quantity, test_mode)
                    positions[symbol] = {
                        "side": "SELL",
                        "entry": price,
                        "stop_loss": price + atr,
                        "take_profit": price - atr * TP_MULTIPLIER,
                        "quantity": quantity
                    }

        except Exception as e:
            logger.error(f"Erro no símbolo {symbol}: {e}")

# ---------------- MAIN LOOP ---------------- #
if __name__ == "__main__":
    while True:
        try:
            # Carrega dados locais para otimização inicial
            df = pd.read_csv("data/sample_ohlcv.csv")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)

            best_params = otimizar_parametros_continuo(df, num_combinations=NUM_COMBINATIONS)
            logger.info(f"[MAIN] Melhor parâmetro encontrado: {best_params.to_dict()}")

            run_live_trading(best_params, test_mode=True)  # set test_mode=False para real

            sleep(SLEEP_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Encerrando AutoTraderPro_Advanced")
            break
        except Exception as e:
            logger.error(f"Erro inesperado no loop principal: {e}")
            sleep(60)
