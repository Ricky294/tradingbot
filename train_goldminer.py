if __name__ == "__main__":
    import math
    from pathlib import Path

    import numpy as np
    import torch as pt
    from torch.nn.modules.loss import CrossEntropyLoss
    from torch.optim import AdamW
    from torch.utils.data import Dataset, DataLoader
    from torch.utils.data.dataset import T_co
    from tqdm import tqdm
    from crypto_data.binance.pd.extract import get_candles
    from crypto_data.binance.schema import *
    from crypto_data.shared.candle_db import CandleDB

    from checkpointing.load import load_model
    from checkpointing.save import save_model
    from nn.models import GoldMiner
    from nn.metrics import accuracy_function, label_accuracy_function
    from metrics import Mean


    def classify(future_series: np.ndarray, take_profit_rate: float):
        future_high_series = future_series[:, 1]
        future_low_series = future_series[:, 2]
        future_high_max = np.max(future_high_series)
        future_low_min = np.min(future_low_series)

        long_profit_hit = future_high_max >= take_profit_rate
        short_profit_hit = future_low_min <= -take_profit_rate

        if long_profit_hit and short_profit_hit:
            long_profit_hit_index = np.where(future_high_series >= take_profit_rate)[0][0]
            short_profit_hit_index = np.where(future_low_series <= -take_profit_rate)[0][0]
            return 2 if long_profit_hit_index < short_profit_hit_index else 1
        elif long_profit_hit:
            return 2
        elif short_profit_hit:
            return 1
        return 0


    class CandleDataset(Dataset):
        def __init__(
                self,
                candle_data,
                history_length: int,
                future_length: int,
                min_profit_rate: float = 0.05
        ):
            raw_data = np.transpose(
                np.lib.stride_tricks.sliding_window_view(
                    candle_data,
                    window_shape=(history_length + future_length,),
                    axis=0
                ),
                axes=(0, 2, 1)
            ).copy()

            price_min = np.min(raw_data[:, :history_length, :4], axis=(-2, -1))[:, np.newaxis, np.newaxis]
            price_max = np.max(raw_data[:, :history_length, :4], axis=(-2, -1))[:, np.newaxis, np.newaxis]
            last_close_prices = raw_data[:, history_length - 1, 3][:, np.newaxis, np.newaxis]
            vol_min = np.min(raw_data[:, :history_length, 4], axis=-1)[:, np.newaxis]
            vol_max = np.max(raw_data[:, :history_length, 4], axis=-1)[:, np.newaxis]
            raw_data[:, :, :4] = (raw_data[:, :, :4] - last_close_prices) / (price_max - price_min)
            raw_data[:, :, 4] = (raw_data[:, :, 4] - vol_min) / (vol_max - vol_min)

            ds = tuple(
                (item[:history_length], item[history_length:])
                for item in raw_data
            )
            ds = tuple(
                (inp_seq, classify(tar_seq, min_profit_rate))
                for inp_seq, tar_seq in ds
            )
            targets = tuple(target for _, target in ds)
            labels = set(targets)
            targets = np.array(tuple(tr for _, tr in ds))
            self.labels = {
                lb: float(np.sum(targets == lb))
                for lb in labels
            }
            self.dataset = ds

        def __getitem__(self, index) -> T_co:
            return self.dataset[index]

        def __len__(self):
            return len(self.dataset)


    symbol = "BTCUSDT"
    interval = "5m"
    market = "FUTURES"

    db_path = Path(".cache", "candles")
    if not db_path.exists():
        db_path.mkdir()
    candle_db = CandleDB(str(db_path.joinpath("binance_candles.db")))
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    )
    candles = candles.to_numpy(dtype="float32")

    epochs = 50
    save_freq = 2
    batch_size = 64
    d_input = 5
    seq_len = 512
    d_hidden = 1024
    n_layers = 4
    device = "cuda"
    model = GoldMiner(
        d_input=d_input,
        seq_len=seq_len,
        d_hidden=d_hidden,
        n_layers=n_layers,
        device=device,
        dropout=0.25
    )
    model.training = True
    optimizer = AdamW(params=model.parameters(), lr=1e-3, eps=1e-7)

    if load_model(model, optimizer):
        print(f"Model {str(model)} loaded successfully . . .")
    else:
        print(f"Model {str(model)} not found. Starting from scratch . . .")

    loss_metric = Mean()
    accuracy_metric = Mean()
    long_acc_metric = Mean()
    short_acc_metric = Mean()
    hold_acc_metric = Mean()
    long_prec_metric = Mean()
    short_prec_metric = Mean()
    hold_prec_metric = Mean()
    long_rec_metric = Mean()
    short_rec_metric = Mean()
    hold_rec_metric = Mean()

    dataset = CandleDataset(
        candle_data=candles[:int(0.7 * len(candles))],
        history_length=seq_len,
        future_length=64,
        min_profit_rate=0.2
    )
    data_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

    weights = pt.tensor([
        (len(dataset) / dataset.labels[0]) if 0 in dataset.labels else 0,
        (len(dataset) / dataset.labels[1] * 1.2) if 1 in dataset.labels else 0,
        (len(dataset) / dataset.labels[2] * 1.2) if 2 in dataset.labels else 0
    ], dtype=pt.float32, device=device)
    loss_obj = CrossEntropyLoss(weight=weights)


    def train_step(input_tensor: pt.Tensor, target_tensor: pt.Tensor):
        y_pred = model(input_tensor)
        y_pred = y_pred.to(device=device)
        target_tensor = target_tensor.to(device=device)

        loss = loss_obj(y_pred, target_tensor)
        accuracy = accuracy_function(target_tensor, y_pred)
        long_accuracy = label_accuracy_function(target_tensor, y_pred, 2)
        short_accuracy = label_accuracy_function(target_tensor, y_pred, 1)
        hold_accuracy = label_accuracy_function(target_tensor, y_pred, 0)
        if not math.isnan(loss.item()):
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            loss_metric(loss.item())
        if not pt.isnan(accuracy):
            accuracy_metric(accuracy)
        if not pt.isnan(long_accuracy):
            long_acc_metric(long_accuracy)
        if not pt.isnan(short_accuracy):
            short_acc_metric(short_accuracy)
        if not pt.isnan(hold_accuracy):
            hold_acc_metric(hold_accuracy)


    data = tuple(enumerate(data_loader))
    for epoch in range(epochs):
        loss_metric.reset()
        accuracy_metric.reset()
        long_acc_metric.reset()
        short_acc_metric.reset()
        hold_acc_metric.reset()
        iterator = tqdm(
            data,
            desc=f"Training epoch: {epoch}",
            unit="batch"
        )
        for batch, (inp, tar) in iterator:
            train_step(inp, tar)
            iterator.postfix = (
                f"loss={loss_metric.result():5.4f} " +
                f"acc={accuracy_metric.result():1.2f} " +
                f"long={long_acc_metric.result():1.2f} " +
                f"short={short_acc_metric.result():1.2f} " +
                f"hold={hold_acc_metric.result():1.2f} "
            )

        if (epoch + 1) % save_freq == 0:
            print(f"Saving model to cache {str(model)} . . .")
            save_model(model, optimizer)
