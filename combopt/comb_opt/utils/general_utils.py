# Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.

# This program is free software; you can redistribute it and/or modify it under
# the terms of the MIT license.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the MIT License for more details.

import os
import pathlib
import pickle
import random
import time
from datetime import datetime
from typing import Any

import matplotlib

matplotlib.use('Agg')

import torch
# import yaml

from typing import Optional, List, Union, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes


def load_yaml(path_to_yaml_file):
    import yaml
    with open(path_to_yaml_file, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(dictionary, save_path):
    import yaml
    with open(save_path, 'w') as file:
        _ = yaml.dump(dictionary, file)


def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False


def create_save_dir(save_dir):
    if os.path.exists(save_dir):
        print(
            f'{current_time_formatter()} - Directory {save_dir} already exists. Continuing with the experiment may lead to previous results being overwritten.')
    os.makedirs(save_dir, exist_ok=True)


def get_path_to_save_dir(settings):
    path = os.path.join(pathlib.Path(__file__).parent.parent.parent.resolve(), "results", settings.get("task_name"),
                        settings.get("problem_name"), settings.get("save_dir"))
    return path


def array_to_tensor(X, device):
    if not isinstance(X, torch.Tensor):
        X = torch.tensor(X, dtype=torch.float32, device=device)
    if X.dim() == 1:
        X = X.reshape(1, -1)

    return X


def copy_tensor(x):
    return torch.empty_like(x).copy_(x)


def save_w_pickle(obj: Any, path: str, filename: Optional[str] = None) -> None:
    """ Save object obj in file exp_path/filename.pkl """
    if filename is None:
        filename = os.path.basename(path)
        path = os.path.dirname(path)
    if len(filename) < 4 or filename[-4:] != '.pkl':
        filename += '.pkl'
    with open(os.path.join(path, filename), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_w_pickle(path: str, filename: Optional[str] = None) -> Any:
    """ Load object from file exp_path/filename.pkl """
    if filename is None:
        filename = os.path.basename(path)
        path = os.path.dirname(path)
    if len(filename) < 4 or filename[-4:] != '.pkl':
        filename += '.pkl'
    with open(os.path.join(path, filename), 'rb') as f:
        try:
            return pickle.load(f)
        except EOFError as e:
            raise e
        except UnicodeDecodeError as e:
            p = os.path.join(path, filename)
            raise Exception(f"UnicodeDecodeError with {p}")


def safe_load_w_pickle(path: str, filename: Optional[str] = None, n_trials=3, time_sleep=2) -> Any:
    """ Make several attempts to load object from file exp_path/filename.pkl """
    trial = 0
    end = False
    result = None
    while not end:
        try:
            result = load_w_pickle(path=path, filename=filename)
            end = True
        except (pickle.UnpicklingError, EOFError) as e:
            trial += 1
            if trial > n_trials:
                raise e
            time.sleep(time_sleep)
        except UnicodeDecodeError as e:
            if filename is None:
                filename = os.path.basename(path)
                path = os.path.dirname(path)
            log(os.path.join(path, filename))
            raise e
    return result


def time_formatter(t: float, show_ms: bool = False) -> str:
    """ Convert a duration in seconds to a str `dd:hh:mm:ss`

    Args:
        t: time in seconds
        show_ms: whether to show ms on top of dd:hh:mm:ss
    """
    n_day = time.gmtime(t).tm_yday - 1
    if n_day > 0:
        ts = time.strftime('%H:%M:%S', time.gmtime(t))
        ts = f"{n_day}:{ts}"
    else:
        ts = time.strftime('%H:%M:%S', time.gmtime(t))
    if show_ms:
        ts += f'{t - int(t):.3f}'.replace('0.', '.')
    return ts


def current_time_formatter():
    return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())


def log(message, header: Optional[str] = None, end: Optional[str] = None):
    if header is None:
        header = ''
    print(f'[{header}' + f' {current_time_formatter()}' + f"]  {message}", end=end)


def cummax(X: np.ndarray, return_ind=False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """ Return array containing at index `i` the value max(X)[:i] """
    cmaxind: List[int] = [0]
    cmax: List[float] = [X[0]]
    for i, x in enumerate(X[1:]):
        i += 1
        if x > cmax[-1]:
            cmax.append(x)
            cmaxind.append(i)
        else:
            cmax.append(cmax[-1])
            cmaxind.append(cmaxind[-1])
    cmax_np = np.array(cmax)
    assert np.all(X[cmaxind] == cmax_np), (X, X[cmaxind], cmax_np)
    if return_ind:
        return cmax_np, np.array(cmaxind)
    return cmax_np


def get_cummax(scores: Union[List[np.ndarray], np.ndarray]) -> List[np.ndarray]:
    """ Compute cumulative max for each array in a list

    Args:
        scores: list of the arrays on which `cummax` will be applied

    Returns:
        cmaxs:
    """
    if not isinstance(scores, list) and isinstance(scores, np.ndarray):
        scores = np.atleast_2d(scores)
    else:
        raise TypeError(f'Expected List[np.ndarray] or np.ndarray, got {type(scores)}')

    cmaxs: List[np.ndarray] = []
    for score in scores:
        cmaxs.append(cummax(score))
    return cmaxs


def get_cummin(scores: Union[List[np.ndarray], np.ndarray]) -> List[np.ndarray]:
    """ Compute cumulative min for each array in a list

    Args:
        scores: list of the arrays on which `cummin` will be applied

    Returns:
        cmins:
    """
    if not isinstance(scores, list) and isinstance(scores, np.ndarray):
        scores = np.atleast_2d(scores)
    else:
        raise TypeError(f'Expected List[np.ndarray] or np.ndarray, got {type(scores)}')
    cmins: List[np.ndarray] = []
    for score in scores:
        cmins.append(-cummax(-score))
    return cmins


def get_common_chunk_sizes(ys: List[np.ndarray]):
    """ From a list of arrays of various sizes, get a list of `list of arrays of same size`

     Example:
         >>> ys = [[1, 3 ,4, 5],
                   [0, 7, 8 , 2, 9],
                   [-1]]
         >>> get_common_chunk_sizes(ys)
         ---> [
         --->   ([0], [[1], [0], [-1]]),               # gather all elements of index in [0]
         --->   ([1, 2, 3], [[3, 4, 5], [7, 8, 2]]),   # gather all elements of index in [1, 2, 3]
         --->   ([4], [[9]])                           # gather all elements of index in [4]
         ---> ]
     """
    ys = [y for y in ys if len(y) > 0]
    lens = [0] + sorted(set([len(y) for y in ys]))

    output = []
    for i in range(1, len(lens)):
        Xs = np.arange(lens[i - 1], lens[i])
        y = [y[lens[i - 1]:lens[i]] for y in ys if len(y) >= lens[i]]
        output.append((Xs, y))
    return output


def plot_mean_std(*args, n_std: Optional[int] = 1,
                  ax: Optional[Axes] = None, alpha: float = .3,
                  **plot_mean_kwargs):
    """ Plot mean and std (with fill between) of sequential data Y of shape (n_trials, lenght_of_a_trial)

    Args:
        X: x-values (if None, we will take `range(0, len(Y))`)
        Y: y-values
        n_std: number of std to plot around the mean (if `0` only the mean is plotted)
        ax: axis on which to plot the curves
        color: color of the curve
        alpha: parameter for `fill_between`

    Returns:
        The axis.
    """
    if len(args) == 1:
        Y = args[0]
        X = None
    elif len(args) == 2:
        X, Y = args
    else:
        raise RuntimeError('Wrong number of arguments (should be [X], Y,...)')

    assert len(Y) > 0, 'Y should be a non-empty array, nothing to plot'
    Y = np.atleast_2d(Y)
    if X is None:
        X = np.arange(Y.shape[1])
    assert X.ndim == 1, f'X should be of rank 1, got {X.ndim}'
    mean = Y.mean(0)
    std = Y.std(0)
    if ax is None:
        ax = plt.subplot()

    line_plot = ax.plot(X, mean, **plot_mean_kwargs)

    if n_std > 0 and Y.shape[0] > 1:
        ax.fill_between(X, mean - n_std * std, mean + n_std * std, alpha=alpha, color=line_plot[0].get_c())

    return ax