from binance.client import Client
from binance.enums import *
import MetaTrader5 as mt5
from utils.logger import get_logger
import pandas as pd

logger = get_logger("BrokerAdapter")

class BrokerAdapter:
    def __init__(self, binance_api_key="", binance_api_secret=""):
        self.client_binance = Client(binance_api_key, binance_api_secret) if binance_api_key else None
        if not mt5.initialize():
            logger.warning("MT5 não inicializado. Ordens MT5 serão ignoradas.")
        self.positions = {}

    def execute_binance_order(self, symbol, side, qty, test_mode=True):
        if test_mode:
            logger.info(f"[BINANCE TEST] {side} {qty} {symbol}")
            return
        try:
            self.client_binance.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=qty)
            logger.info(f"[BINANCE] Ordem executada {side} {qty} {symbol}")
        except Exception as e:
            logger.error(f"[BINANCE] Erro na ordem: {e}")

    def get_ohlcv(self, symbol, interval="1h", limit=200):
        if not self.client_binance:
            return pd.DataFrame()
        data = self.client_binance.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(data, columns=[
            "timestamp","open","high","low","close","volume","close_time",
            "quote_asset_volume","num_trades","taker_base_vol","taker_quote_vol","ignore"
        ])
        df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['timestamp','open','high','low','close','volume']]

    def get_balance(self, asset="USDT"):
        if not self.client_binance:
            return 0
        account_info = self.client_binance.get_account()
        for b in account_info['balances']:
            if b['asset'] == asset:
                return float(b['free'])
        return 0

    def execute_mt5_order(self, symbol, action, lot, test_mode=True):
        if test_mode:
            logger.info(f"[MT5 TEST] {action} {lot} {symbol}")
            return
        if not mt5.initialize():
            logger.error("MT5 não inicializado. Ordem ignorada.")
            return
        order_type = mt5.ORDER_TYPE_BUY if action=="BUY" else mt5.ORDER_TYPE_SELL
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.error(f"[MT5] Não foi possível obter preço de {symbol}")
            return
        price = tick.ask if action=="BUY" else tick.bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "deviation": 10,
            "magic": 42,
            "comment": "AutoTraderPro",
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        res = mt5.order_send(request)
        if res.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"[MT5] Erro: {res}")
        else:
            logger.info(f"[MT5] Ordem executada {action} {lot} {symbol}")
