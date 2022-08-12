import torch

from comb_opt.search_space import SearchSpace
from comb_opt.optimizers.bocs import BOCS

if __name__ == '__main__':
    # Create a search space with only binary variables
    non_binary_search_space = SearchSpace([{'name': 'var 1', 'type': 'nominal', 'categories': ['A', 'B', 'C']},
                                           {'name': 'var 2', 'type': 'bool'},
                                           {'name': 'var 3', 'type': 'bool'},
                                           {'name': 'var 4', 'type': 'bool'}], dtype=torch.float32)

    binary_search_space = SearchSpace([{'name': 'var 1', 'type': 'bool'},
                                       {'name': 'var 2', 'type': 'bool'},
                                       {'name': 'var 3', 'type': 'bool'},
                                       {'name': 'var 4', 'type': 'bool'}], dtype=torch.float32)

    print('Initialising BOCS with a non-binary search space - no warning should be printed')
    BOCS(non_binary_search_space, n_init=10)

    print('Initialising BOCS with a binary search space - this should print a warning')
    BOCS(binary_search_space, n_init=10)
