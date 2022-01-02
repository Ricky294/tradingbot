import numpy as np

from consts.actions import BUY, SELL, NONE
from consts.candle_column_index import CLOSE_PRICE_INDEX
from indicator import Indicator
from model import Order
from strategy import Strategy
from abstract import FuturesTrader
from util.trade import calculate_quantity


class SimpleStrategy(Strategy):
    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            indicator: Indicator
    ):
        super().__init__(symbol=symbol, trader=trader)
        self.indicator = indicator

    def __call__(
            self,
            candles: np.ndarray,
    ):
        result = self.indicator.result(candles)
        latest_rsi = result.tail(1)

        if latest_rsi["buy_signal"].item():
            signal = BUY
        elif latest_rsi["sell_signal"].item():
            signal = SELL
        else:
            signal = NONE

        if signal != NONE and self.trader.get_position(self.symbol) is None:
            self.trader.cancel_orders(self.symbol)

            latest_close = candles[-1][CLOSE_PRICE_INDEX]
            quantity = calculate_quantity(
                side=signal,
                balance=self.trader.get_balances()["USDT"],
                leverage=self.trader.get_leverage(self.symbol),
                price=latest_close,
                percentage=self.trader.trade_ratio,
            )

            stop_loss_price = (
                latest_close - 400 if signal == BUY else latest_close + 400
            )
            take_profit_price = (
                latest_close - 400 if signal == SELL else latest_close + 400
            )

            self.trader.create_position(
                Order.market(
                    symbol=self.symbol,
                    quantity=quantity,
                ),
                Order.take_profit_market(
                    symbol=self.symbol,
                    stop_price=take_profit_price,
                ),
                Order.stop_market(
                    symbol=self.symbol,
                    stop_price=stop_loss_price,
                ),
            )
