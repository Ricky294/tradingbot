import numpy as np

from trader.core.interface import FuturesTrader
from trader.core.const.trade_actions import SELL, BUY
from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from checkpointing.load import load_model
from nn.models.miner import Miner
from strategy import Strategy


class AIStrategy(Strategy):

    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            trade_ratio: float,
            leverage=1,
            asset="USDT",
    ):
        super().__init__(symbol=symbol, trader=trader, leverage=leverage, trade_ratio=trade_ratio, asset=asset)
        self.model = Miner(d_input=256, d_hidden=2048, n_layers=8, device="cuda")
        load_model(self.model)

    def __call__(
            self,
            candles: np.ndarray,
    ):
        logits = self.model(candles.T[CLOSE_PRICE_INDEX][-256:][None, :], training=False)
        logits = logits.to("cpu").detach().numpy()
        signal = np.argmax(logits)

        if signal is not None and self.trader.get_position(self.symbol) is None:
            self.trader.cancel_orders(self.symbol)

            latest_close = candles[-1][CLOSE_PRICE_INDEX]
            quantity = self.get_quantity(
                signal=signal,
                price=latest_close,
            )

            stop_loss_price = (
                latest_close - 1000 if signal == BUY else latest_close + 1000
            )
            take_profit_price = (
                latest_close - 1000 if signal == SELL else latest_close + 1000
            )

            self.enter_position(
                quantity=quantity,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
            )
