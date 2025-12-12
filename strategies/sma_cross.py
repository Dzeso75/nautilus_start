# strategies/sma_cross.py
from nautilus_trader.model.data import Bar
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.core.nautilus_pyo3.indicators import SimpleMovingAverage


class SMACross(Strategy):
    def __init__(self, bar_type, fast_period: int = 10, slow_period: int = 20):
        super().__init__()
        self.bar_type = bar_type
        self.instrument_id = bar_type.instrument_id
        self.fast_sma = SimpleMovingAverage(fast_period)
        self.slow_sma = SimpleMovingAverage(slow_period)
        self.position_open = False

    def on_start(self):
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar: Bar):
        self.fast_sma.update_raw(bar.close)
        self.slow_sma.update_raw(bar.close)

        if not self.fast_sma.initialized or not self.slow_sma.initialized:
            return

        if self.fast_sma.value > self.slow_sma.value and not self.position_open:
            # Buy signal
            order = MarketOrder(
                trader_id=self.trader_id,
                strategy_id=self.id,
                instrument_id=self.instrument_id,
                order_side=1,  # BUY
                quantity=self.risk_manager.get_quantity(self.instrument_id),
                time_in_force=3,  # GTC
            )
            self.submit_order(order)
            self.position_open = True

        elif self.fast_sma.value < self.slow_sma.value and self.position_open:
            # Sell signal
            order = MarketOrder(
                trader_id=self.trader_id,
                strategy_id=self.id,
                instrument_id=self.instrument_id,
                order_side=2,  # SELL
                quantity=self.risk_manager.get_quantity(self.instrument_id),
                time_in_force=3,
            )
            self.submit_order(order)
            self.position_open = False