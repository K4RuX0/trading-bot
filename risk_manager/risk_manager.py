import numpy as np

class RiskManager:
    def __init__(self, capital=10000.0, risk_per_trade=0.01, min_lot=0.001):
        self.capital = float(capital)
        self.risk_per_trade = float(risk_per_trade)
        self.min_lot = min_lot

    def position_size(self, price: float, stop_distance: float):
        if stop_distance <= 0 or price <= 0:
            return self.min_lot
        risk_amount = self.capital * self.risk_per_trade
        size = risk_amount / stop_distance
        return max(size, self.min_lot)

    def batch_position_size(self, prices: np.ndarray, stop_distances: np.ndarray):
        prices = np.array(prices, dtype=float)
        stops = np.array(stop_distances, dtype=float)
        valid = (stops > 0) & (prices > 0)
        sizes = np.full_like(prices, fill_value=self.min_lot, dtype=float)
        sizes[valid] = (self.capital * self.risk_per_trade) / stops[valid]
        return np.maximum(sizes, self.min_lot)
