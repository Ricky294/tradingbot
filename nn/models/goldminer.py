import torch as pt
import pickle
from torch.nn import Module, Linear, Dropout, TransformerEncoder, TransformerEncoderLayer, Conv1d
from torch.nn import functional as F
from hashlib import sha256
from encoding.time import TimeEncoder
from nn.layers import Time2Vec


class Goldminer(Module):
    def __init__(
            self,
            d_input: int,
            seq_len: int,
            d_hidden: int,
            n_layers: int,
            device: str,
            dropout: float = 0.25
    ):
        super(Goldminer, self).__init__()
        self.__d_input = d_input
        self.__seq_len = seq_len
        self.__d_hidden = d_hidden
        self.__n_layers = n_layers
        self.__d_hidden_embed = 256
        self.__device = device
        self.__time_encoding = pt.tensor(
            TimeEncoder()(self.__seq_len, self.__d_input, 0.01).T,
            device=self.__device
        )
        self.time_embedding = Time2Vec(
            self.__seq_len,
            self.__d_hidden,
            bias=True,
            device=device,
            dtype=pt.float32
        )
        self.conv_layer = Conv1d(
            self.__d_hidden,
            self.__seq_len,
            kernel_size=(1,),
            stride=(1,),
            device=self.__device,
            dtype=pt.float32
        )
        self.trans_encoder = TransformerEncoder(
            TransformerEncoderLayer(
                self.__d_input,
                nhead=1,
                dim_feedforward=512,
                dropout=dropout,
                activation=F.gelu,
                layer_norm_eps=1e-5,
                batch_first=True,
                device=device,
                dtype=pt.float32
            ),
            num_layers=self.__n_layers
        )
        self.time_embed_dropout = Dropout(dropout, inplace=True)
        self.trans_encoder_dropout = Dropout(dropout, inplace=True)
        self.conv_dropout = Dropout(dropout, inplace=True)
        self.reducer = Linear(self.__d_input, 1, bias=True, device=self.__device, dtype=pt.float32)
        self.clz_layer = Linear(self.__seq_len, 3, bias=True, device=self.__device, dtype=pt.float32)

    def forward(self, series):
        x = series.to(self.__device)
        x += self.__time_encoding
        x = pt.transpose(self.time_embedding(pt.transpose(x, -1, -2)), -1, -2)
        x = self.time_embed_dropout(x)
        x = self.conv_layer(x)
        x = self.conv_dropout(x)
        x = self.trans_encoder(x)
        x = self.trans_encoder_dropout(x)
        x = self.reducer(x)
        x = pt.squeeze(x, dim=-1)
        out = self.clz_layer(x)
        return out

    @property
    def config(self):
        return {
            "name": self.__class__.__name__,
            "d_input": self.__d_input,
            "seq_len": self.__seq_len,
            "d_hidden": self.__d_hidden,
            "n_layers": self.__n_layers,
            "d_hidden_embed": self.__d_hidden_embed,
            "device": self.__device
        }

    def __str__(self):
        return sha256(
            pickle.dumps(self.config) +
            Goldminer.forward.__code__.co_code
        ).hexdigest()
