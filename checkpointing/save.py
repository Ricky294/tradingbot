import torch as pt

from torch.nn import Module
from torch.optim import Optimizer

from checkpointing import save_path


def save_model(model: Module, optimizer: Optimizer):
    model_name = str(model)
    checkpoint_path = save_path.joinpath(model_name)

    pt.save(
        {
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
        },
        checkpoint_path
    )

    print("Model saved.")
