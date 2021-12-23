import numpy as np

from typing import Dict

from consts.actions import BUY, SELL, NONE
from consts.candle_column_index import CLOSE_PRICE_INDEX
from indicator import Indicator
from model import Balance, SymbolTradeInfo, Order
from strategy import Strategy
from abstract import FuturesTrader
from util.trade import calculate_quantity


class RSIStrategy(Strategy):
    def __init__(
        self, symbol: str, trader: FuturesTrader, rsi_indicator: Indicator
    ):
        super().__init__(symbol=symbol, trader=trader)
        self.rsi_indicator = rsi_indicator

    def on_candle(
        self,
        candles: np.ndarray,
        trade_info: SymbolTradeInfo,
        balances: Dict[str, Balance],
    ):
        result = self.rsi_indicator.result(candles)
        latest_rsi = result.tail(1)

        signal = NONE
        if latest_rsi["buy_signal"].item():
            signal = BUY
        elif latest_rsi["sell_signal"].item():
            signal = SELL

        if signal != NONE and self.trader.get_position(trade_info.symbol) is None:
            self.trader.cancel_orders(trade_info.symbol)

            latest_close = candles[-1][CLOSE_PRICE_INDEX]
            quantity = calculate_quantity(
                side=signal,
                balance=balances["USDT"],
                leverage=self.trader.get_leverage(trade_info.symbol),
                price=latest_close,
                percentage=self.trader.trade_ratio,
            )

            stop_loss_price = (
                latest_close - 1000 if signal == BUY else latest_close + 1000
            )
            take_profit_price = (
                latest_close - 1000 if signal == SELL else latest_close + 1000
            )

            self.trader.create_orders(
                Order.market(
                    symbol=trade_info.symbol,
                    quantity=quantity,
                ),
                Order.take_profit_market(
                    symbol=trade_info.symbol,
                    quantity=-quantity,
                    stop_price=take_profit_price,
                ),
                Order.stop_market(
                    symbol=trade_info.symbol,
                    quantity=-quantity,
                    stop_price=stop_loss_price,
                ),
            )
