import numpy as np

import tree_paths
from binomial_tree import BinomialTree


def test_is_discounted_asset_price_martingale():
    nb_periods = 120
    mean, std = 6e-4, 1.04e-2
    div_periods = np.array([53, 117, 181, 242])
    div_periods = div_periods[div_periods <= nb_periods]
    div_yield = 5e-3 * np.ones_like(div_periods)
    rate, s0 = 0.009 / nb_periods, 64.94
    bin_tree = BinomialTree(nb_periods, mean, std, rate, s0, div_yield=div_yield, div_periods=div_periods)
    omega = np.random.choice([-1, 1], nb_periods)

    bin_tree.generate()

    assert np.isclose(tree_paths.extract(bin_tree.tree, omega)[:-1],
                      bin_tree.calculate_expectation(omega)).all()
