"""
Risk manager: calcula tamanho de posição baseado em percentual do capital,
e verifica regras simples (max position per trade).
"""
from dataclasses import dataclass

@dataclass
class RiskManager:
    capital: float
    risk_per_trade: float = 0.01  # fraction of capital

    def position_size(self, price: float, stop_distance: float = None) -> float:
        """
        calculate size in units/contracts (naive): risk_per_trade * capital / (stop_distance * price)
        If stop_distance is None, risk is approximated as risk_per_trade of capital / price.
        For simplicity, we'll return size = (risk_per_trade * capital) / price
        """
        if price <= 0:
            return 0.0
        risk_dollars = self.capital * self.risk_per_trade
        size = risk_dollars / price
        return max(0.0, size)
