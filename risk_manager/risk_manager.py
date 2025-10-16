import numpy as np

class RiskManager:
    def __init__(self, capital=10000, risk_per_trade=0.01, min_lot=0.001):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.min_lot = min_lot

    def position_size(self, price, stop_distance):
        if price <= 0 or stop_distance <= 0:
            return self.min_lot
        risk_amount = self.capital * self.risk_per_trade
        size = risk_amount / stop_distance
        return max(size, self.min_lot)
