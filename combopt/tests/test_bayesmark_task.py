# Copyright (C) 2022. Huawei Technologies Co., Ltd. All rights reserved. Redistribution and use in source and binary
# forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
from pathlib import Path

ROOT_PROJECT = str(Path(os.path.realpath(__file__)).parent.parent)
sys.path[0] = ROOT_PROJECT

import torch

from comb_opt.optimizers import RandomSearch
from comb_opt.utils.plotting_utils import plot_convergence_curve

if __name__ == "__main__":
    from comb_opt.factory import task_factory

    for model_name in ["DT", "lasso"]:
        for database_id, metric in zip(["breast", "boston"], ["nll", "mae"]):
            task, search_space = task_factory('bayesmark', torch.float32, model_name=model_name,
                                              database_id=database_id, metric=metric)

            optimizer = RandomSearch(search_space, store_observations=True)
            print(f"{optimizer.name}_{task.name}")

            for i in range(10):
                x_next = optimizer.suggest(5)
                y_next = task(x_next)
                optimizer.observe(x_next, y_next)
                print(f'Iteration {i + 1:>4d} - Best f(x) {optimizer.best_y:.3f}')

            plot_convergence_curve(optimizer, task,
                                   os.path.join(Path(os.path.realpath(__file__)).parent.parent.resolve(),
                                                f'{optimizer.name}_{task.name}_test.png'), plot_per_iter=True)