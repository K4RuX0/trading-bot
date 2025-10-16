import numpy as np

class RiskManager:
    def __init__(self, capital=10000.0, risk_per_trade=0.01, min_lot=0.001):
        if capital <= 0:
            raise ValueError("capital deve ser positivo")
        if not (0 < risk_per_trade <= 1):
            raise ValueError("risk_per_trade deve estar entre 0 e 1")
        self.capital = float(capital)
        self.risk_per_trade = float(risk_per_trade)
        self.min_lot = min_lot

    def position_size(self, price: float, stop_distance: float):
        if stop_distance <= 0 or price <= 0:
            return self.min_lot
        risk_amount = self.capital * self.risk_per_trade
        size = risk_amount / stop_distance
        return max(size, self.min_lot)
