from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import StrategyConfig


class MACDConfig(StrategyConfig):
    """Configuration for MACD strategy."""

    instrument_id: InstrumentId
    fast_period: int = 12
    slow_period: int = 26
    trade_size: int = 10000