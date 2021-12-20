import torch as pt

from torch.nn import Module
from torch.optim import Optimizer

from checkpointing import save_path


def load_model(model: Module, optimizer: Optimizer = None):
    model_name = str(model)
    checkpoint_path = save_path.joinpath(model_name)

    if checkpoint_path.exists():
        checkpoint = pt.load(checkpoint_path)
        model.load_state_dict(checkpoint["model_state"])
        if optimizer is not None:
            model.load_state_dict(checkpoint["optimizer_state"])
        print("Model loaded.")
    else:
        print("Model not found.")
