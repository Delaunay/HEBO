import torch

from comb_opt.factory import task_factory
from comb_opt.models.gp.exact_gp import ExactGPModel
from comb_opt.models.gp.kernels import DiffusionKernel
from comb_opt.utils.graph_utils import laplacian_eigen_decomposition
from comb_opt.utils.plotting_utils import plot_model_prediction

if __name__ == '__main__':
    dtype = torch.float64
    device = torch.device('cpu')
    task, search_space = task_factory('sphere', dtype, num_dims=10, variable_type='nominal', num_categories=10)

    x_train_pd = search_space.sample(1000)
    x_train = search_space.transform(x_train_pd)
    y_train = torch.tensor(task(x_train_pd))

    x_test_pd = search_space.sample(200)
    x_test = search_space.transform(x_test_pd)
    y_test = torch.tensor(task(x_test_pd))

    n_vertices, adjacency_matrix_list, fourier_frequency_list, fourier_basis_list = laplacian_eigen_decomposition(
        search_space)

    kernel = DiffusionKernel(fourier_frequency_list, fourier_basis_list)

    model = ExactGPModel(search_space, 1, kernel)

    model.fit(x_train, y_train)

    plot_model_prediction(model, x_test, y_test, './model_pred.png')
