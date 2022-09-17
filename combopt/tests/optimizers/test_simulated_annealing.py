import os
from pathlib import Path
import sys

ROOT_PROJECT = str(Path(os.path.realpath(__file__)).parent.parent)
sys.path[0] = ROOT_PROJECT

import torch

from comb_opt.optimizers.simulated_annealing import SimulatedAnnealing
from comb_opt.utils.plotting_utils import plot_convergence_curve

if __name__ == '__main__':
    from comb_opt.factory import task_factory

    task, search_space = task_factory('levy', torch.float32, num_dims=10, variable_type='nominal', num_categories=21)

    optimizer = SimulatedAnnealing(search_space, allow_repeating_suggestions=False)

    for i in range(500):
        x_next = optimizer.suggest(1)
        y_next = task(x_next)
        optimizer.observe(x_next, y_next)
        print(f'Iteration {i + 1:>4d} - f(x) {optimizer.best_y:.3f}')

    plot_convergence_curve(optimizer, task, os.path.join(Path(os.path.realpath(__file__)).parent.parent.resolve(),
                                                         f'{optimizer.name}_test.png'), plot_per_iter=True)