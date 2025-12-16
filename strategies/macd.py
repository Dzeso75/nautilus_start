from configs.macd import MACDConfig

from nautilus_trader.core.message import Event
from nautilus_trader.indicators import MovingAverageConvergenceDivergence
from nautilus_trader.model import Position
from nautilus_trader.model import Quantity
from nautilus_trader.model import QuoteTick
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.events import PositionClosed
from nautilus_trader.model.events import PositionOpened
from nautilus_trader.trading.strategy import Strategy


class MACDStrategy(Strategy):
    """A MACD-based strategy that only trades on zero-line crossovers."""

    def __init__(self, config: MACDConfig):
        super().__init__(config=config)
        # Our "trading signal"
        self.macd = MovingAverageConvergenceDivergence(
            fast_period=config.fast_period, slow_period=config.slow_period, price_type=PriceType.MID
        )

        self.trade_size = Quantity.from_int(config.trade_size)

        # Track our position and MACD state
        self.position: Position | None = None
        self.last_macd_above_zero = None  # Track if MACD was above zero on last check

    def on_start(self):
        """Subscribe to market data on strategy start."""
        self.subscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_stop(self):
        """Clean up on strategy stop."""
        self.close_all_positions(self.config.instrument_id)
        self.unsubscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_quote_tick(self, tick: QuoteTick):
        """Process incoming quote ticks."""
        # Update indicator
        self.macd.handle_quote_tick(tick)

        if not self.macd.initialized:
            return  # Wait for indicator to warm up

        # Check for trading opportunities
        self.check_signals()

    def on_event(self, event: Event):
        """Handle position events."""
        if isinstance(event, PositionOpened):
            self.position = self.cache.position(event.position_id)
            if self.position is not None:
                self._log.info(f"Position opened: {self.position.side} @ {self.position.avg_px_open}")
            else:
                self._log.warning("Position opened event received, but position not found in cache.")
        elif isinstance(event, PositionClosed):
            if self.position and self.position.id == event.position_id:
                self._log.info(f"Position closed with PnL: {self.position.realized_pnl}")
                self.position = None

    def check_signals(self):
        """Check MACD signals - only act on actual crossovers."""
        current_macd = self.macd.value
        current_above_zero = current_macd > 0

        # Skip if this is the first reading
        if self.last_macd_above_zero is None:
            self.last_macd_above_zero = current_above_zero
            return

        # Only act on actual crossovers
        if self.last_macd_above_zero != current_above_zero:
            if current_above_zero:  # Just crossed above zero
                # Only go long if we're not already long
                if not self.is_long:
                    # Close any short position first
                    if self.is_short:
                        self.close_position(self.position)
                    # Then go long (but only when flat)
                    self.go_long()

            else:  # Just crossed below zero
                # Only go short if we're not already short
                if not self.is_short:
                    # Close any long position first
                    if self.is_long:
                        self.close_position(self.position)
                    # Then go short (but only when flat)
                    self.go_short()

        self.last_macd_above_zero = current_above_zero

    def go_long(self):
        """Enter long position only if flat."""
        if self.is_flat:
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.trade_size,
            )
            self.submit_order(order)
            self._log.info(f"Going LONG - MACD crossed above zero: {self.macd.value:.6f}")

    def go_short(self):
        """Enter short position only if flat."""
        if self.is_flat:
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                quantity=self.trade_size,
            )
            self.submit_order(order)
            self._log.info(f"Going SHORT - MACD crossed below zero: {self.macd.value:.6f}")

    @property
    def is_flat(self) -> bool:
        """Check if we have no position."""
        return self.position is None

    @property
    def is_long(self) -> bool:
        """Check if we have a long position."""
        return self.position is not None and self.position.side == PositionSide.LONG

    @property
    def is_short(self) -> bool:
        """Check if we have a short position."""
        return self.position is not None and self.position.side == PositionSide.SHORT

    def on_dispose(self):
        """Clean up on strategy disposal."""