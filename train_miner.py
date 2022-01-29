import matils

import numpy as np
import torch as pt
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import *
from crypto_data.shared.candle_db import CandleDB
from torch.nn.modules.loss import CrossEntropyLoss
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.dataset import T_co

from numpy.lib.stride_tricks import sliding_window_view

from tqdm import tqdm

from shared.const.candle_index import CLOSE_PRICE_INDEX
from checkpointing.load import load_model
from checkpointing.save import save_model
from nn.models import Miner
from nn.metrics import accuracy_function, label_accuracy_function

from metrics import Mean


epochs = 50
batch_size = 128
d_input = 256
device = "cuda"
save_freq = 5

symbol = "BTCUSDT"
interval = "5m"
market = "FUTURES"
skip = d_input

candle_db = CandleDB("data/binance_candles.db")
candles = get_candles(
    symbol=symbol,
    interval=interval,
    market=market,
    db=candle_db,
    columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
)
candles = candles.to_numpy().T

close_prices = candles[CLOSE_PRICE_INDEX]

model = Miner(d_input=d_input, d_hidden=2048, n_layers=8, device=device)
optimizer = AdamW(params=model.parameters(), lr=1e-4, eps=1e-9)

load_model(model, optimizer)
# np.sum(np.array(tuple(item for el in tuple(enumerate(data_loader)) for item in el[1][1])) == 2)
size = 167770
buy_size = 7942
sell_size = 7952
hold_size = 151876

loss_obj = CrossEntropyLoss(
    weight=pt.tensor([
        size / hold_size,
        size / sell_size,
        size / buy_size,
    ], dtype=pt.float32, device=device)
)
loss_metric = Mean()
accuracy_metric = Mean()
buy_acc_metric = Mean()
sell_acc_metric = Mean()
hold_acc_metric = Mean()


class SingleSeriesDataset(Dataset):

    def __init__(self, data, history_length: int, future_length: int):
        raw_data = sliding_window_view(data, window_shape=(history_length + future_length,))
        ds = tuple(
            (item[:history_length], item[history_length:])
            for item in raw_data
        )
        ds = tuple(
            (inp_seq, classify(inp_seq[-1], tar_seq, 1000))
            for inp_seq, tar_seq in ds
        )
        self.dataset = ds

    def __getitem__(self, index) -> T_co:
        return self.dataset[index]

    def __len__(self):
        return len(self.dataset)


def train_step(input_tensor: pt.Tensor, target_tensor: pt.Tensor):
    y_pred = model(input_tensor, training=True)
    y_pred = y_pred.to(device=device)
    target_tensor = target_tensor.to(device=device)

    loss = loss_obj(y_pred, target_tensor)
    accuracy = accuracy_function(target_tensor, y_pred)
    buy_accuracy = label_accuracy_function(target_tensor, y_pred, 2)
    sell_accuracy = label_accuracy_function(target_tensor, y_pred, 1)
    hold_accuracy = label_accuracy_function(target_tensor, y_pred, 0)
    if not matils.isnan(loss.item()):
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        loss_metric(loss.item())
    if not pt.isnan(accuracy):
        accuracy_metric(accuracy)
    if not pt.isnan(buy_accuracy):
        buy_acc_metric(buy_accuracy)
    if not pt.isnan(sell_accuracy):
        sell_acc_metric(sell_accuracy)
    if not pt.isnan(hold_accuracy):
        hold_acc_metric(hold_accuracy)


def classify(current_close: float, future_close_series: np.ndarray, take_profit: float):
    future_close_max = np.max(future_close_series)
    future_close_min = np.min(future_close_series)

    long_profit_hit = future_close_max >= current_close + take_profit
    short_profit_hit = future_close_min <= current_close - take_profit

    if long_profit_hit and short_profit_hit:
        long_profit_hit_index = np.where(future_close_series >= current_close + take_profit)[0][0]
        short_profit_hit_index = np.where(future_close_series <= current_close - take_profit)[0][0]

        return 2 if long_profit_hit_index < short_profit_hit_index else 1
    elif long_profit_hit:
        return 2
    elif short_profit_hit:
        return 1
    return 0


dataset = SingleSeriesDataset(
    data=close_prices[:int(0.7 * len(close_prices))],
    history_length=d_input,
    future_length=64
)
data_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)


for epoch in range(epochs):
    data = tuple(enumerate(data_loader))
    iterator = tqdm(
        data,
        desc=f"Training epoch: {epoch}",
        unit="batch"
    )
    for batch, (inp, tar) in iterator:
        train_step(inp, tar)
        iterator.postfix = (
            f"loss={loss_metric.result():5.2f} ",
            f"acc={accuracy_metric.result():1.2f} ",
            f"buy={buy_acc_metric.result():1.2f} ",
            f"sell={sell_acc_metric.result():1.2f} ",
            f"hold={hold_acc_metric.result():1.2f} ",
        )

    if (epoch + 1) % save_freq == 0:
        save_model(model, optimizer)
