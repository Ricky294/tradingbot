import re

from model.order import (
    generate_client_order_id,
    limit_order_with_stop_loss_take_profit,
    market_order_with_stop_loss_take_profit,
)


def test_multi_order():
    symbol = "BTCUSDT"
    quantity = 0.001
    price = 60_000
    stop_price = 58_000
    take_profit_price = 62_000

    # Limit + stop loss order + take profit order

    orders = limit_order_with_stop_loss_take_profit(
        symbol=symbol,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        profit_price=take_profit_price,
    )

    order = orders["order"].to_binance_order()
    stop_order = orders["stop_order"].to_binance_order()
    profit_order = orders["profit_order"].to_binance_order()

    assert order == {
        "symbol": symbol,
        "side": "BUY",
        "quantity": str(quantity),
        "type": "LIMIT",
        "timeInForce": "GTC",
        "price": str(price),
    }

    assert stop_order == {
        "symbol": symbol,
        "side": "SELL",
        "type": "STOP_MARKET",
        "closePosition": "true",
        "stopPrice": str(stop_price),
    }

    assert profit_order == {
        "symbol": symbol,
        "side": "SELL",
        "type": "TAKE_PROFIT_MARKET",
        "closePosition": "true",
        "stopPrice": str(take_profit_price),
    }

    # Market + stop loss order

    quantity = -0.001
    orders = market_order_with_stop_loss_take_profit(
        symbol=symbol,
        quantity=quantity,
        stop_price=stop_price,
    )

    order = orders["order"].to_binance_order()
    stop_order = orders["stop_order"].to_binance_order()
    assert "profit_order" not in orders

    assert order == {
        "symbol": symbol,
        "side": "SELL",
        "quantity": str(abs(quantity)),
        "type": "MARKET",
    }

    assert stop_order == {
        "symbol": symbol,
        "side": "BUY",
        "type": "STOP_MARKET",
        "closePosition": "true",
        "stopPrice": str(stop_price),
    }


def test_generate_client_order_id():

    for _ in range(100):
        cid = generate_client_order_id()
        assert re.search(r"^[.A-Z:/a-z0-9_-]{1,36}$", cid)
