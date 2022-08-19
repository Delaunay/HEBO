from comb_opt.factory import task_factory
from comb_opt.optimizers.mix_and_match.gp_ssk_kernel_tr_ga_acq_optim import GpSskTrGaAcqOptim

if __name__ == '__main__':
    task, search_space = task_factory('ackley', num_dims=20, variable_type='nominal', num_categories=5)

    optimiser = GpSskTrGaAcqOptim(search_space, 10, tr_verbose=True)

    n = 2000
    for i in range(n):
        x_next = optimiser.suggest()
        y_next = task(x_next)
        optimiser.observe(x_next, y_next)
        print(f"Iteration {i + 1:03d}/{n} Current value: {y_next[0, 0]:.2f} - best value: {optimiser.best_y:.2f}")
