import numpy as np
import pytest

import options
import tree_paths
from binomial_tree import BinomialTree


@pytest.fixture(scope="module")
def setup_parameters():
    nb_periods = 126
    mean, std = 6e-4, 1.04e-2
    div_periods = np.array([53, 117, 181, 242])
    div_periods = div_periods[div_periods <= nb_periods]
    div_yield = 5e-3 * np.ones_like(div_periods)
    rate, s0 = 4e-5, 64.94
    omega = np.random.choice([-1, 1], nb_periods)
    tree = BinomialTree(nb_periods, mean, std, rate, s0, div_yield=div_yield, div_periods=div_periods)
    tree.generate()
    return tree, omega, s0


def test_is_american_put_excess_process_non_decreasing(setup_parameters):
    tree, omega, strike = setup_parameters
    option = options.american_put
    analyzer = options.Analyzer(tree, option, strike=strike)

    mtg, excess = analyzer.decompose_envelope(omega=omega)

    assert (np.diff(excess) >= 0).all()


def test_is_american_call_excess_process_zero(setup_parameters):
    tree, omega, strike = setup_parameters
    option = options.american_call
    analyzer = options.Analyzer(tree, option, strike=strike)

    mtg, excess = analyzer.decompose_envelope(omega=omega)

    assert (np.diff(excess) == 0).all()


def test_is_european_call_envelope_martingale(setup_parameters):
    tree, omega, strike = setup_parameters
    option = options.european_call

    analyzer = options.Analyzer(tree, option, strike=strike)

    assert np.isclose(tree_paths.extract(analyzer.envelope_tree, omega)[:-1],
                      tree.calculate_expectation(omega, tree=analyzer.envelope_tree)).all()


def test_is_european_put_envelope_martingale(setup_parameters):
    tree, omega, strike = setup_parameters
    option = options.european_put

    analyzer = options.Analyzer(tree, option, strike=strike)

    assert np.isclose(tree_paths.extract(analyzer.envelope_tree, omega)[:-1],
                      tree.calculate_expectation(omega, tree=analyzer.envelope_tree)).all()
