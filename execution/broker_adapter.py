"""
Broker adapter genérico.
- Se BROKER_NAME == 'SIMULATED' ou PAPER==True -> usa simulação local.
- Para brokers reais: implementar métodos send_order, cancel_order, etc.
"""

import uuid
from dataclasses import dataclass
from typing import Dict, Any
from config import broker_cfg
from risk.risk_manager import RiskManager

@dataclass
class Order:
    id: str
    side: str
    price: float
    size: float
    status: str

class BrokerAdapter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.orders = {}
        # For paper/simulated we track balances simply
        self.sim_balances = {"USD": 10000.0}
        self.sim_positions = {}
        # TODO: if connecting to real broker, init client here using cfg.API_KEY, etc.

    def place_order(self, side: str, price: float, size: float) -> Order:
        """
        For simulated broker we create an order and mark it FILLED immediately.
        Real broker logic would use API calls.
        """
        order_id = str(uuid.uuid4())
        order = Order(id=order_id, side=side, price=price, size=size, status="FILLED" if self.cfg.PAPER else "CREATED")
        self.orders[order_id] = order
        return order

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id].status = "CANCELLED"
            return True
        return False

    def get_order(self, order_id: str) -> Order:
        return self.orders.get(order_id)

    def calculate_size(self, cash: float, price: float, risk_per_trade: float) -> float:
        # Simple wrapper to risk manager
        rm = RiskManager(capital=cash, risk_per_trade=risk_per_trade)
        return rm.position_size(price)
