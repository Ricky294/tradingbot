from backtest import BacktestPosition


def test_long_position():
    bp = BacktestPosition(
        entry_time=1,
        entry_price=100,
        entry_quantity=1,
        leverage=1
    )

    assert 100 == bp.calculate_profit(200)

    bp.adjust(2, 200, 1)

    assert 100 == bp.calculate_profit(200)
    assert 500 == bp.calculate_profit(400)


def test_short_position():
    bp = BacktestPosition(
        entry_time=1,
        entry_price=100,
        entry_quantity=-1,
        leverage=1
    )

    assert -100 == bp.calculate_profit(200)

    bp.adjust(2, 200, -1)

    assert -100 == bp.calculate_profit(200)
    assert -500 == bp.calculate_profit(400)

