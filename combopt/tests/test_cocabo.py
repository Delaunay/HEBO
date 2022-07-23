import os
from pathlib import Path

import torch

from comb_opt.optimizers.cocabo import CoCaBO
from comb_opt.utils.plotting_utils import plot_convergence_curve

if __name__ == '__main__':
    from comb_opt.factory import task_factory

    task, search_space = task_factory('levy', torch.float32, num_dims=[5, 5], variable_type=['nominal', 'num'],
                                      num_categories=[21, None])

    optimiser = CoCaBO(search_space, n_init=20, device=torch.device('cpu'))

    for i in range(100):
        x_next = optimiser.suggest(1)
        y_next = task(x_next)
        optimiser.observe(x_next, y_next)
        print(f'Iteration {i + 1:>4d} - f(x) {optimiser.best_y:.3f}')

    plot_convergence_curve(optimiser, task, os.path.join(Path(os.path.realpath(__file__)).parent.parent.resolve(),
                                                         f'{optimiser.name}_test.png'), plot_per_iter=True)