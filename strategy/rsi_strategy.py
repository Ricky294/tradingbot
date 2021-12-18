import pandas as pd

from typing import Dict

from crypto_data.binance.schema import CLOSE_PRICE

from indicator import RSIIndicator
from model import Balance, SymbolTradeInfo, Order
from strategy import SingleSymbolStrategy
from abstract import FuturesTrader
from trade_util import calculate_quantity


class RSIStrategy(SingleSymbolStrategy):
    def __init__(
        self, symbol: str, trader: FuturesTrader, rsi: RSIIndicator, leverage: int = 1
    ):
        symbol = symbol.upper()
        super().__init__(symbol=symbol, trader=trader)
        self.rsi = rsi
        self.trader.set_leverage(symbol, leverage)

    def on_candle(
        self,
        candles: pd.DataFrame,
        trade_info: SymbolTradeInfo,
        balances: Dict[str, Balance],
    ):
        result = self.rsi.result(candles)
        latest_rsi = result.tail(1)

        signal = None
        if latest_rsi["buy_signal"].item():
            signal = "BUY"
        elif latest_rsi["sell_signal"].item():
            signal = "SELL"

        if signal is not None and self.trader.get_position(trade_info.symbol) is None:
            self.trader.cancel_orders(trade_info.symbol)

            latest_close = candles.tail(1)[CLOSE_PRICE].item()
            quantity = calculate_quantity(
                side=signal,
                balance=balances["USDT"],
                leverage=self.trader.get_leverage(trade_info.symbol),
                price=latest_close,
                percentage=self.trader.trade_ratio,
            )

            stop_loss_price = (
                latest_close - 1000 if signal == "BUY" else latest_close + 1000
            )
            take_profit_price = (
                latest_close - 1000 if signal == "SELL" else latest_close + 1000
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
