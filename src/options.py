import functools

import numpy as np

from tree_paths import extract as extract_path
from binomial_tree import BinomialTree


class Analyzer:

    def __init__(self, tree: BinomialTree, payoff_func, **option_params):
        self.tree = tree
        self.payoff_tree = tree.calculate_payoff_tree(payoff_func, **option_params)
        self.envelope_tree = tree.calculate_envelope_tree(self.payoff_tree)

    def decompose_envelope(self, omega, all_processes=False):
        # get envelope for given path
        envelope = extract_path(self.envelope_tree, omega)
        # calculate its expectations
        expectations = self.tree.calculate_expectation(omega, tree=self.envelope_tree)
        # calculate excess and put 0 at the beginning
        excess = np.hstack((0, np.cumsum(envelope[:-1] - expectations)))
        # having excess constructed we can find mtg by adding envelope (U = M -A => M = U + A)
        mtg = envelope + excess
        # To avoid extracting envelope second time while finding stopping times, returning it is allowed
        if all_processes:
            return mtg, excess, envelope
        else:
            return mtg, excess

    def find_stopping_times(self, omega):
        # get payoff for given path
        payoff = extract_path(self.payoff_tree, omega)
        # get envelope for given path and its decomposition
        mtg, excess, envelope = self.decompose_envelope(omega, all_processes=True)
        try:
            # tau_max if there was a moment when excess process raised
            tau_max = np.argwhere(excess > 0)[0]
        except IndexError:
            # if excess process =0, then tau_max="number of periods" (for example length of excess process)
            tau_max = len(excess) - 1

        return np.argwhere(payoff == envelope), tau_max


def european_discount(func):
    @functools.wraps(func)
    def wrapper_european_discount(asset_price, rate, **kwargs):
        # strike is  the only obligatory keyword argument
        kwargs['strike'] /= np.exp(rate * (asset_price.shape[0] - 1))
        return func(asset_price, rate, **kwargs)

    return wrapper_european_discount


def american_discount(func):
    @functools.wraps(func)
    def wrapper_american_discount(asset_price, rate, **kwargs):
        # strike is  the only obligatory keyword argument
        size = asset_price.shape[0]
        kwargs['strike'] = kwargs['strike'] / np.exp(rate * np.array([np.arange(size), ] * size))
        return func(asset_price, rate, **kwargs)

    return wrapper_american_discount


@european_discount
def european_call(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[:, -1] = np.maximum(asset_price[:, -1] - strike, 0)
    return payoff_tree


@european_discount
def european_put(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[:, -1] = np.maximum(strike - asset_price[:, -1], 0)
    return payoff_tree


@american_discount
def american_call(asset_price, rate, strike):
    return np.maximum(asset_price - strike, 0)


@american_discount
def american_put(asset_price, rate, strike):
    return np.maximum(strike - asset_price, 0)


@european_discount
def european_binary_call(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    (payoff_tree[:, -1])[asset_price[:, -1] >= strike] = 1
    return payoff_tree


@european_discount
def european_binary_put(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    (payoff_tree[:, -1])[asset_price[:, -1] <= strike] = 1
    return payoff_tree


@american_discount
def american_binary_call(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[asset_price >= strike] = 1
    return payoff_tree


@american_discount
def american_binary_put(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[asset_price <= strike] = 1
    return payoff_tree


@european_discount
def european_asset_or_nothing_call(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    positive_payoff = (asset_price[:, -1])[asset_price[:, -1] >= strike]
    (payoff_tree[:, -1])[asset_price[:, -1] >= strike] = positive_payoff
    return payoff_tree


@european_discount
def european_asset_or_nothing_put(asset_price, rate, strike):
    payoff_tree = np.zeros_like(asset_price)
    positive_payoff = (asset_price[:, -1])[asset_price[:, -1] <= strike]
    (payoff_tree[:, -1])[asset_price[:, -1] <= strike] = positive_payoff
    return payoff_tree


@american_discount
def american_asset_or_nothing_call(asset_price, rate, strike):
    payoff_tree = np.copy(asset_price)
    payoff_tree[payoff_tree < strike] = 0
    return payoff_tree


@american_discount
def american_asset_or_nothing_put(asset_price, strike):
    payoff_tree = np.copy(asset_price)
    payoff_tree[payoff_tree > strike] = 0
    return payoff_tree
