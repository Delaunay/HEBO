# Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.

# This program is free software; you can redistribute it and/or modify it under
# the terms of the MIT license.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the MIT License for more details.

import copy
import warnings
from typing import Optional

import numpy as np
import torch
from torch.quasirandom import SobolEngine

from comb_opt.acq_funcs import AcqBase
from comb_opt.acq_optimizers import AcqOptimizerBase
from comb_opt.models import ModelBase
from comb_opt.optimizers.multi_armed_bandit import MultiArmedBandit
from comb_opt.search_space import SearchSpace
from comb_opt.search_space.search_space import SearchSpaceSubSet
from comb_opt.trust_region import TrManagerBase
from comb_opt.utils.discrete_vars_utils import get_discrete_choices
from comb_opt.utils.discrete_vars_utils import round_discrete_vars
from comb_opt.utils.model_utils import add_hallucinations_and_retrain_model
from comb_opt.utils.data_buffer import DataBuffer


class MabAcqOptimizer(AcqOptimizerBase):

    def __init__(self,
                 search_space: SearchSpace,
                 acq_func: AcqBase,
                 batch_size: int = 1,
                 max_n_iter: int = 200,
                 mab_resample_tol: int = 500,
                 n_cand: int = 5000,
                 n_restarts: int = 5,
                 cont_optimizer: str = 'adam',
                 cont_lr: float = 1e-3,
                 cont_n_iter: int = 100,
                 dtype: torch.dtype = torch.float32,
                 ):

        assert search_space.num_dims == search_space.num_cont + search_space.num_disc + search_space.num_nominal + search_space.num_ordinal, \
            'The Mixed MAB acquisition optimizer does not support permutation variables.'

        assert n_cand >= n_restarts, \
            'The number of random candidates must be > number of points selected for gradient based optimisation'

        super(MabAcqOptimizer, self).__init__(search_space, dtype)

        self.acq_func = acq_func
        self.n_cats = [int(ub + 1) for ub in search_space.nominal_ub]
        self.n_cand = n_cand
        self.n_restarts = n_restarts
        self.cont_optimizer = cont_optimizer
        self.cont_lr = cont_lr
        self.cont_n_iter = cont_n_iter
        self.batch_size = batch_size

        # Algorithm initialisation
        if search_space.num_cont > 0:
            seed = np.random.randint(int(1e6))
            self.sobol_engine = SobolEngine(search_space.num_numeric, scramble=True, seed=seed)

        self.mab_search_space = SearchSpaceSubSet(search_space, nominal_dims=True, ordinal_dims=True, dtype=dtype)
        self.mab = MultiArmedBandit(search_space=self.mab_search_space,
                                    batch_size=batch_size,
                                    max_n_iter=max_n_iter,
                                    noisy_black_box=True,
                                    resample_tol=mab_resample_tol,
                                    dtype=dtype)

        self.numeric_dims = self.search_space.cont_dims + self.search_space.disc_dims
        self.cat_dims = np.sort(self.search_space.nominal_dims + self.search_space.ordinal_dims).tolist()

        # Dimensions of discrete variables in tensors containing only numeric variables
        self.disc_dims_in_numeric = [i + len(self.search_space.cont_dims) for i in
                                     range(len(self.search_space.disc_dims))]

        self.discrete_choices = get_discrete_choices(search_space)

        self.inverse_mapping = [(self.numeric_dims + self.cat_dims).index(i) for i in range(self.search_space.num_dims)]

    def optimize(self,
                 x: torch.Tensor,
                 n_suggestions: int,
                 x_observed: torch.Tensor,
                 model: ModelBase,
                 acq_func: AcqBase,
                 acq_evaluate_kwargs: dict,
                 tr_manager: Optional[TrManagerBase],
                 **kwargs
                 ) -> torch.Tensor:

        assert (self.n_restarts == 0 and self.n_cand >= n_suggestions) or (self.n_restarts >= n_suggestions)

        if tr_manager is not None:
            raise RuntimeError("MAB does not support TR for now")  # TODO: handle TR

        if self.batch_size != n_suggestions:
            warnings.warn('batch_size used for initialising the algorithm is not equal to n_suggestions received by' + \
                          ' the acquisition optimizer. If the batch size is known in advance, consider initialising' + \
                          ' the acquisition optimizer with the correct batch size for better performance.')

        x_next = torch.zeros((0, self.search_space.num_dims), dtype=self.dtype)

        if n_suggestions > 1:
            # create a local copy of the model
            model = copy.deepcopy(model)
        else:
            model = model

        if self.search_space.num_nominal > 0 and self.search_space.num_cont > 0:

            x_cat = self.mab_search_space.transform(self.mab.suggest(n_suggestions))

            x_cat_unique, x_cat_counts = torch.unique(x_cat, return_counts=True, dim=0)

            for idx, curr_x_cat in enumerate(x_cat_unique):

                if len(x_next):
                    # Add the last point to the model and retrain it
                    add_hallucinations_and_retrain_model(model, x_next[-x_cat_counts[idx - 1].item()])

                x_numeric_ = self.optimize_x_numeric(curr_x_cat, x_cat_counts[idx], model, acq_evaluate_kwargs)
                x_cat_ = curr_x_cat * torch.ones((x_cat_counts[idx], curr_x_cat.shape[0]))

                x_next = torch.cat((x_next, self.reconstruct_x(x_numeric_, x_cat_)))

        elif self.search_space.num_cont > 0:
            x_next = torch.cat((x_next, self.optimize_x_numeric(torch.tensor([]), n_suggestions, acq_func)))

        elif self.search_space.num_nominal > 0:
            x_next = torch.cat((x_next, self.sample_nominal(n_suggestions)))

        return x_next

    def optimize_x_numeric(self, x_cat: torch.Tensor,
                           n_suggestions: int,
                           model: ModelBase,
                           acq_evaluate_kwargs: dict,
                           ):

        # Make a copy of the acquisition function if necessary to avoid changing original model parameters
        if n_suggestions > 1:
            model = copy.deepcopy(model)

        output = torch.zeros((0, self.search_space.num_numeric), dtype=self.dtype)

        for i in range(n_suggestions):

            if len(output) > 0:
                add_hallucinations_and_retrain_model(model, self.reconstruct_x(output[-1], x_cat))

            # Sample x_cont
            x_numeric_cand = self.sobol_engine.draw(self.n_cand)  # Note that this assumes x in [0, 1]

            x_cand = self.reconstruct_x(x_numeric_cand, x_cat * torch.ones((self.n_cand, x_cat.shape[0])))

            # Evaluate all random samples
            with torch.no_grad():
                acq = self.acq_func(x_cand, model, **acq_evaluate_kwargs)

            if self.n_restarts > 0:

                x_cont_best = None
                best_acq = None

                x_local_cand = x_cand[acq.argsort()[:self.n_restarts]]

                for x_ in x_local_cand:

                    x_numeric_, x_cat_ = x_[self.numeric_dims], x_[self.search_space.nominal_dims]
                    x_numeric_.requires_grad_(True)

                    if self.cont_optimizer == 'adam':
                        optimizer = torch.optim.Adam([{"params": x_numeric_}], lr=self.cont_lr)
                    elif self.cont_optimizer == 'sgd':
                        optimizer = torch.optim.SGD([{"params": x_numeric_}], lr=self.cont_lr)
                    else:
                        raise NotImplementedError(f'optimizer {self.num_optimizer} is not implemented.')

                    for _ in range(self.cont_n_iter):
                        optimizer.zero_grad()
                        x_cand = self.reconstruct_x(x_numeric_, x_cat_)
                        acq_x = self.acq_func(x_cand, model, **acq_evaluate_kwargs)

                        try:
                            acq_x.backward()
                            optimizer.step()
                        except RuntimeError:
                            print('Exception occurred during backpropagation. NaN encountered?')
                            pass
                        with torch.no_grad():
                            x_numeric_.data = round_discrete_vars(x_numeric_, self.disc_dims_in_numeric,
                                                                  self.discrete_choices)
                            x_numeric_.data = torch.clip(x_numeric_, min=0, max=1)

                    x_numeric_.requires_grad_(False)

                    if best_acq is None or acq_x < best_acq:
                        best_acq = acq_x.item()
                        x_cont_best = x_numeric_

            else:
                x_cont_best = x_numeric_cand[acq.argsort()[0]]

            output = torch.cat((output, x_cont_best.unsqueeze(0)))

        return output

    def reconstruct_x(self, x_numeric: torch.Tensor, x_cat: torch.Tensor) -> torch.Tensor:
        if x_numeric.ndim == x_cat.ndim == 1:
            return torch.cat((x_numeric, x_cat))[self.inverse_mapping]
        else:
            return torch.cat((x_numeric, x_cat), dim=1)[:, self.inverse_mapping]

    def post_observe_method(self, x: torch.Tensor, y: torch.Tensor, data_buffer: DataBuffer, n_init: int, **kwargs):
        """
        Function used to update the weights of each of the multi-armed bandit agents.

        :param x:
        :param y:
        :param data_buffer:
        :param n_init:
        :param kwargs:
        :return:
        """
        if len(data_buffer) < n_init:
            return
        elif len(data_buffer) == n_init:
            x_cat_init = self.mab_search_space.inverse_transform(data_buffer.x[:, self.cat_dims])
            y_init = data_buffer.y.cpu().numpy()
            self.mab.initialize(x_cat_init, y_init)
            return

        x_cat = self.mab_search_space.inverse_transform(x[:, self.cat_dims])
        y = y.cpu().numpy()

        self.mab.observe(x_cat, y)
