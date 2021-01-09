import numpy as np

import tree_paths
from binomial_tree import BinomialTree


def test_is_discounted_asset_price_martingale():
    nb_periods = 126
    mean, std = 6e-4, 1.04e-2
    div_periods = np.array([53, 117, 181, 242])
    div_periods = div_periods[div_periods <= nb_periods]
    div_yield = 5e-3 * np.ones_like(div_periods)
    rate, s0 = 4e-5, 64.94
    tree = BinomialTree(nb_periods, mean, std, rate, s0, div_yield=div_yield, div_periods=div_periods)
    omega = np.random.choice([-1, 1], nb_periods)

    tree.generate()

    assert np.isclose(tree_paths.extract(tree.tree, omega)[:-1],
                      tree.calculate_expectation(omega)).all()
