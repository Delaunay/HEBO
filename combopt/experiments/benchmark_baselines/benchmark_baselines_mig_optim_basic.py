import os
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(os.path.realpath(__file__)).parent.parent.parent))

from comb_opt.factory import task_factory
from comb_opt.optimizers import RandomSearch, LocalSearch, SimulatedAnnealing, BOCS, BOSS, COMBO, \
    Casmopolitan, BOiLS, PymooGeneticAlgorithm
from comb_opt.utils.experiment_utils import run_experiment

if __name__ == '__main__':
    task_name = 'mig_optimization'
    task_kwargs = {'ntk_name': "sqrt", "objective": "both"}
    bo_n_init = 20
    bo_device = torch.device('cuda:0')
    max_num_iter = 200
    dtype = torch.float32
    random_seeds = [42, 43, 44, 45, 46]

    task, search_space = task_factory(task_name, dtype, **task_kwargs)

    rs_optim = RandomSearch(search_space=search_space, dtype=dtype)
    ls_optim = LocalSearch(search_space=search_space, dtype=dtype)
    sa_optim = SimulatedAnnealing(search_space=search_space, dtype=dtype)
    ga_optim = PymooGeneticAlgorithm(search_space=search_space, dtype=dtype)
    bocs = BOCS(search_space=search_space, n_init=bo_n_init, dtype=dtype, device=bo_device)
    boss = BOSS(search_space=search_space, n_init=bo_n_init, model_max_batch_size=50, dtype=dtype, device=bo_device)
    combo = COMBO(search_space=search_space, n_init=bo_n_init, dtype=dtype, device=bo_device)
    casmopolitan = Casmopolitan(search_space=search_space, n_init=bo_n_init, dtype=dtype, device=bo_device)
    boils = BOiLS(search_space=search_space, n_init=bo_n_init, model_max_batch_size=50, dtype=dtype, device=bo_device)

    optimizers = [
        # boss,
        # boils,
        # casmopolitan,
        # combo,
        # bocs,
        # mab_optim,
        # rs_optim,
        # ls_optim,
        # sa_optim,
        # ga_optim
    ]

    run_experiment(task=task, optimizers=optimizers, random_seeds=random_seeds, max_num_iter=max_num_iter,
                   very_verbose=False)
