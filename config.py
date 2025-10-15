import os
from typing import Optional

class BrokerConfig:
    """Configurações do broker."""
    PAPER: bool = True
    BROKER_NAME: str = 'SIMULATED'
    API_KEY: Optional[str] = os.environ.get("API_KEY")  # Usando variável de ambiente
    API_SECRET: Optional[str] = os.environ.get("API_SECRET")  # Usando variável de ambiente
    COMMISSION: float = 0.001  # Taxa de corretagem (0.1%)

broker_cfg = BrokerConfig()

class StrategyConfig:
    """Configurações da estratégia de trading."""
    FAST_WINDOW: int = 10
    SLOW_WINDOW: int = 50
    RISK_PER_TRADE: float = 0.01
    INITIAL_CAPITAL: float = 10000.0
    STOP_LOSS: float = 0.02  # Stop loss padrão (2%)
    TAKE_PROFIT: float = 0.05 # Take profit padrão (5%)
    ATR_MULTIPLIER: float = 2.0  # Multiplicador para stop loss baseado em ATR
    USE_ATR_STOP_LOSS: bool = False # Usar stop loss baseado em ATR ou percentual

strategy_cfg = StrategyConfig()

class BotConfig:
    """Configurações gerais do bot."""
    MODE: str = "backtest"
    DATA_FILE: str = "data/sample_ohlcv.csv"
    LOG_LEVEL: str = "INFO"  # Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

bot_cfg = BotConfig()

# Exemplo de como acessar as configurações
if __name__ == '__main__':
    print(f"Modo do Bot: {bot_cfg.MODE}")
    print(f"Capital Inicial: {strategy_cfg.INITIAL_CAPITAL}")
    print(f"Broker: {broker_cfg.BROKER_NAME}")
    print(f"Stop Loss: {strategy_cfg.STOP_LOSS}")
    print(f"Take Profit: {strategy_cfg.TAKE_PROFIT}")