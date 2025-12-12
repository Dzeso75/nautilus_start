# tests/test_sma_cross.py
import pytest
from unittest.mock import Mock, patch

from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AggregationSource, BarAggregation, OrderSide, PriceType
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.core.nautilus_pyo3.indicators import SimpleMovingAverage
from strategies.sma_cross import SMACross


@pytest.fixture
def instrument_id():
    return InstrumentId(Symbol("AAPL"), Venue("SIM"))


@pytest.fixture
def bar_type(instrument_id):
    return BarType.from_str(f"{instrument_id}-1-MINUTE[LAST]-EXTERNAL")


def test_sma_cross_submits_buy_order_on_cross_above(bar_type):
    # Arrange
    strategy = SMACross(bar_type=bar_type, fast_period=2, slow_period=3)
    
    # Подменяем зависимости (изолируем стратегию)
    strategy.register_base(
        trader_id=Mock(),
        portfolio=Mock(),
        msgbus=Mock(),
        cache=Mock(),
        risk_engine=Mock(),
        log=Mock(),
    )
    strategy.submit_order = Mock()  # Перехватываем вызовы отправки ордера

    # Подготовим бары так, чтобы произошёл сигнал BUY
    # Нужно: fast_sma > slow_sma после инициализации
    bars = [
        Bar(bar_type, Price(1.00, 2), Price(1.00, 2), Price(1.00, 2), Price(1.00, 2), Quantity(100), 0, 0),
        Bar(bar_type, Price(1.01, 2), Price(1.01, 2), Price(1.01, 2), Price(1.01, 2), Quantity(100), 0, 0),
        Bar(bar_type, Price(1.02, 2), Price(1.02, 2), Price(1.02, 2), Price(1.02, 2), Quantity(100), 0, 0),
        Bar(bar_type, Price(1.03, 2), Price(1.03, 2), Price(1.03, 2), Price(1.03, 2), Quantity(100), 0, 0),
    ]

    # Act
    for bar in bars:
        strategy.on_bar(bar)

    # Assert
    # После 4 баров: fast_sma (2-период) = (1.02 + 1.03)/2 = 1.025
    # slow_sma (3-период) = (1.01 + 1.02 + 1.03)/3 ≈ 1.02
    # => fast > slow → должен быть BUY
    assert strategy.submit_order.call_count == 1
    submitted_order = strategy.submit_order.call_args[0][0]
    assert submitted_order.side == OrderSide.BUY


def test_sma_cross_does_not_trade_before_indicator_ready(bar_type):
    # Arrange
    strategy = SMACross(bar_type=bar_type, fast_period=2, slow_period=3)
    strategy.register_base(
        trader_id=Mock(),
        portfolio=Mock(),
        msgbus=Mock(),
        cache=Mock(),
        risk_engine=Mock(),
        log=Mock(),
    )
    strategy.submit_order = Mock()

    # Подадим только 2 бара — индикаторы ещё не готовы
    bars = [
        Bar(bar_type, Price(1.00, 2), Price(1.00, 2), Price(1.00, 2), Price(1.00, 2), Quantity(100), 0, 0),
        Bar(bar_type, Price(1.01, 2), Price(1.01, 2), Price(1.01, 2), Price(1.01, 2), Quantity(100), 0, 0),
    ]

    # Act
    for bar in bars:
        strategy.on_bar(bar)

    # Assert
    strategy.submit_order.assert_not_called()