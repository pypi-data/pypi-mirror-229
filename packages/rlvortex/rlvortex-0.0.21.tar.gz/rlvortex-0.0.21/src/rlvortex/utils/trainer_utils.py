import torch
import torch.backends.mps
import numpy as np
import random

from typing import Union


def v_debug():
    import pdb

    pdb.set_trace()


def get_available_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_global_random_seed(rd_seed: int = 314):
    random.seed(rd_seed)
    np.random.seed(rd_seed)
    torch.manual_seed(rd_seed)
    torch.cuda.manual_seed(rd_seed)
    torch.cuda.manual_seed_all(rd_seed)
    torch.use_deterministic_algorithms(True)


"""
scale action from range [-1,1] to range [low,high]
"""


def scale_actions(actions: Union[np.ndarray, torch.Tensor], low, high):
    if isinstance(actions, np.ndarray):
        return np.clip((actions + 1) * (high - low) / 2 + low, low, high)
    elif isinstance(actions, torch.Tensor):
        return torch.clamp((actions + 1) * (high - low) / 2 + low, low, high)
    raise ValueError("Unsupported type of actions: {}".format(type(actions)))


"""
unscale action from range [low,high] to range [-1,1]
"""


def unscale_actions(actions: Union[np.ndarray, torch.Tensor], low, high):
    if isinstance(actions, np.ndarray):
        return np.clip((actions - low) * 2 / (high - low) - 1, -1, 1)
    elif isinstance(actions, torch.Tensor):
        return torch.clamp((actions - low) * 2 / (high - low) - 1, -1, 1)
    raise ValueError("Unsupported type of actions: {}".format(type(actions)))
