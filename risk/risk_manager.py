from dataclasses import dataclass

@dataclass
class RiskManager:
    capital: float
    risk_per_trade: float = 0.01  # fraction of capital
    max_position_size: float = 0.1  # max fraction of capital to use in a single trade

    def position_size(self, price: float, stop_distance: float = None) -> float:
        """
        calculate size in units/contracts: risk_per_trade * capital / (stop_distance * price)
        If stop_distance is None, risk is approximated as risk_per_trade of capital / price.
        We'll limit the position size to max_position_size * capital
        """
        if price <= 0:
            return 0.0

        risk_dollars = self.capital * self.risk_per_trade
        if stop_distance:
            size = risk_dollars / (stop_distance * price)
        else:
            size = risk_dollars / price

        # Limit the position size
        max_size = self.capital * self.max_position_size
        size = min(size, max_size)
        return size