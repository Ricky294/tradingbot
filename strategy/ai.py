from typing import Dict

import numpy as np

from abstract import FuturesTrader
from consts.actions import SELL, BUY
from consts.candle_column_index import CLOSE_PRICE_INDEX
from checkpointing.load import load_model
from model import SymbolTradeInfo, Balance, Order
from nn.models.miner import Miner
from strategy import Strategy
from util.trade import calculate_quantity


class AIStrategy(Strategy):

    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
    ):
        super().__init__(symbol, trader)
        self.model = Miner(d_input=256, d_hidden=2048, n_layers=8, device="cuda")
        load_model(self.model)

    def on_candle(
            self,
            candles: np.ndarray,
            trade_info: SymbolTradeInfo,
            balances: Dict[str, Balance],
    ):
        logits = self.model(candles.T[CLOSE_PRICE_INDEX][-256:][None, :], training=False)
        logits = logits.to("cpu").detach().numpy()
        signal = np.argmax(logits)

        if signal is not None and self.trader.get_position(trade_info.symbol) is None:
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
