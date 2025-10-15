import pandas as pd
from typing import Dict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.logger import get_logger
from config import broker_cfg
import numpy as np

logger = get_logger("backtester")

class Backtester:
    def __init__(self, df: pd.DataFrame, signal_generator, initial_capital: float = 10000.0, stop_loss: float = 0.02, take_profit: float = 0.05, atr_multiplier: float = 2.0, use_atr_stop_loss: bool = False):
        print(f"Backtester.__init__ recebendo: initial_capital={initial_capital}, stop_loss={stop_loss}, take_profit={take_profit}, atr_multiplier={atr_multiplier}, use_atr_stop_loss={use_atr_stop_loss}")
        self.df = df
        self.signal_generator = signal_generator
        self.initial_capital = initial_capital
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.atr_multiplier = atr_multiplier
        self.use_atr_stop_loss = use_atr_stop_loss
        self.equity = [initial_capital]
        self.close_prices = []
        self.positions = []  # Lista para rastrear as posições abertas
        self.logger = logger  # Usando o logger configurado
        self.commission = broker_cfg.COMMISSION  # Taxa de corretagem

    def _calculate_size(self, cash, price, risk_per_trade):
        """Calcula o tamanho da posição com base no capital e no risco."""
        try:
            size = (cash * risk_per_trade) / price
            return size
        except ZeroDivisionError:
            self.logger.error("Erro: Preço é zero. Impossível calcular o tamanho da posição.")
            return 0

    def run(self, risk_per_trade: float = 0.01) -> Dict:
        equity = self.initial_capital
        cash = self.initial_capital
        positions = 0
        buys = []
        sells = []
        self.equity = []
        self.close_prices = []
        self.positions = []  # Inicializa a lista de posições

        for idx, row in self.df.iterrows():
            signal = self.signal_generator.on_candle(self.df.loc[:idx])
            price = row['close']
            self.close_prices.append(price)

            # Gerenciar posições existentes (stop loss e take profit)
            for i, pos in enumerate(self.positions):
                if self.use_atr_stop_loss:
                    atr = self.signal_generator.calculate_atr(self.df.loc[:idx]).iloc[-1]
                    atr = atr if not np.isnan(atr) else 0  # Trata NaN
                    stop_loss_level = pos["entry_price"] - self.atr_multiplier * atr
                    if price <= stop_loss_level or price >= pos["entry_price"] * (1 + self.take_profit):
                        # Fechar a posição
                        if positions > 0:
                            equity += price * positions
                            sells.append(price)
                            positions = 0
                            self.positions.clear()  # Limpa a lista de posições
                        elif positions < 0:
                            equity -= price * positions
                            buys.append(price)
                            positions = 0
                            self.positions.clear()  # Limpa a lista de posições
                else:
                    if price <= pos["entry_price"] * (1 - self.stop_loss) or price >= pos["entry_price"] * (1 + self.take_profit):
                        # Fechar a posição
                        if positions > 0:
                            equity += price * positions
                            sells.append(price)
                            positions = 0
                            self.positions.clear()  # Limpa a lista de posições
                        elif positions < 0:
                            equity -= price * positions
                            buys.append(price)
                            positions = 0
                            self.positions.clear()  # Limpa a lista de posições

            if signal == "BUY":
                if positions == 0:
                    # Calcula o tamanho da posição com base no risk_per_trade
                    size = (cash * risk_per_trade) / price
                    positions = size
                    cash -= price * size
                    buys.append(price)
                    self.positions.append({"entry_price": price, "size": size})  # Adiciona a posição à lista
            elif signal == "SELL":
                if positions > 0:
                    equity += price * positions
                    sells.append(price)
                    positions = 0
                    self.positions.clear()  # Limpa a lista de posições

            total_value = equity + positions * price
            self.equity.append(total_value)

        total_return = (equity - self.initial_capital) / self.initial_capital
        # Sharpe ratio (aproximação)
        returns = pd.Series(self.equity).pct_change().dropna()
        sharpe_approx = returns.mean() / returns.std() if returns.std() > 0 else 0

        # Max drawdown
        peak = np.maximum.accumulate(self.equity)
        drawdown = (self.equity - peak) / peak
        max_drawdown = np.min(drawdown) if len(self.equity) > 0 else 0

        results = {
            "initial_capital": self.initial_capital,
            "final_equity": equity,
            "total_return": total_return,
            "sharpe_approx": sharpe_approx,
            "max_drawdown": max_drawdown,
            "n_trades": len(buys) + len(sells),
        }
        return results

    def plot_equity_curve(self, filename=None):
        plt.figure(figsize=(10,5))
        plt.plot(self.df['timestamp'], self.equity, label='Equity Curve')
        plt.xlabel('Time')
        plt.ylabel('Equity')
        plt.title('Backtest Equity Curve')
        plt.legend()
        plt.tight_layout()
        if filename:
            plt.savefig(filename)  # Salva a figura em um arquivo
        else:
            plt.show()
        plt.close()  # Fecha a figura para liberar memória

    def plot_close_price(self): # Nova função para plotar o preço de fechamento
        plt.figure(figsize=(10,5))
        plt.plot(self.df['timestamp'], self.close_prices, label='Close Price')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Close Price Chart')
        plt.legend()
        plt.tight_layout()
        plt.show()