import functools

import numpy as np

import tree_paths
from binomial_tree import BinomialTree
from binomial_tree import BinomialTreeForBarrierPut
from icecream import ic


class Analyzer:

    def __init__(self, prices_tree: BinomialTree, payoff_func, **option_params):
        self.prices_tree = prices_tree
        self.payoff_tree = prices_tree.calculate_payoff_tree(payoff_func, **option_params)
        self.envelope_tree = prices_tree.calculate_envelope_tree(self.payoff_tree)

    def decompose_envelope(self, path, all_processes=False):
        # get envelope for given path
        envelope = tree_paths.extract(self.envelope_tree, path)
        # calculate its expectations
        expectations = self.prices_tree.calculate_expectation(path, tree=self.envelope_tree)
        # calculate excess and put 0 at the beginning
        excess = np.hstack((0, np.cumsum(envelope[:-1] - expectations)))
        # having excess constructed we can find mtg by adding envelope (U = M -A => M = U + A)
        mtg = envelope + excess
        # To avoid extracting envelope second time while finding stopping times, returning it is allowed
        if all_processes:
            return mtg, excess, envelope
        else:
            return mtg, excess

    def find_stopping_times(self, path):
        # get payoff for given path
        payoff = tree_paths.extract(self.payoff_tree, path)
        # get envelope for given path and its decomposition
        mtg, excess, envelope = self.decompose_envelope(path, all_processes=True)
        try:
            # tau_max if there was a moment when excess process raised
            tau_max = np.squeeze(np.argwhere(excess > 0))[0] - 1
        except IndexError:
            # if excess process =0, then tau_max="number of periods" (for example length of excess process)
            tau_max = len(excess) - 1

        return np.squeeze(np.argwhere(payoff == envelope)), tau_max

    def find_replicating_strategy(self):
        # matrix of differences between higher and lower price at certain time
        divisor = -np.diff(self.prices_tree.tree[:, 1:], axis=0)
        # fill redundant entries with ones to avoid division by 0
        divisor[np.tril_indices(divisor.shape[0], -1)] = 1
        # calculate ksi_0
        ksi_0 = np.array([self._cross_diff(U[i:i + 2], X[i:i + 2])
                          for U, X in zip(self.envelope_tree[:, 1:].T, self.prices_tree.tree[:, 1:].T)
                          for i in range(len(U) - 1)])
        ksi_0 = ksi_0.reshape(self.prices_tree.tree[1:, 1:].shape).T / divisor
        # calculate ksi_1
        ksi_1 = -np.diff(self.envelope_tree[:, 1:], axis=0) / divisor
        return ksi_0, ksi_1

    @staticmethod
    def _cross_diff(u, x):
        return u[1] * x[0] - u[0] * x[1]


class BarrierPutAnalyzer:

    def __init__(self, put_prices_tree: BinomialTreeForBarrierPut, bermuda_periods):
        self.put_prices_tree = put_prices_tree
        self.payoff_tree = put_prices_tree.calculate_payoff_tree(bermuda_periods)
        self.envelope_tree = put_prices_tree.calculate_envelope_tree(self.payoff_tree)

    def decompose_envelope(self, path, all_processes=False):
        # get envelope for given path
        envelope = tree_paths.extract(self.envelope_tree, path)
        min_path = self.put_prices_tree.find_min_path()
        path_diff = np.cumsum(path) - np.cumsum(min_path)
        try:
            barrier_id = np.where(path_diff < 0)[0][0]
        except IndexError:
            barrier_id = 0
        else:
            envelope[barrier_id:] = 0
        # calculate its expectations
        expectations = self.put_prices_tree.calculate_expectation(path, tree=self.envelope_tree)
        if barrier_id != 0:
            expectations[barrier_id:] = 0
        # calculate excess and put 0 at the beginning
        excess = np.hstack((0, np.cumsum(envelope[:-1] - expectations)))
        # having excess constructed we can find mtg by adding envelope (U = M -A => M = U + A)
        mtg = envelope + excess
        # To avoid extracting envelope second time while finding stopping times, returning it is allowed
        if all_processes:
            return mtg, excess, envelope
        else:
            return mtg, excess

    def find_stopping_times(self, path):
        # get payoff for given path
        payoff = tree_paths.extract(self.payoff_tree, path)
        # get envelope for given path and its decomposition
        mtg, excess, envelope = self.decompose_envelope(path, all_processes=True)
        try:
            # tau_max if there was a moment when excess process raised
            tau_max = np.squeeze(np.argwhere(excess > 0))[0] - 1
        except IndexError:
            # if excess process =0, then tau_max="number of periods" (for example length of excess process)
            tau_max = len(excess) - 1

        return np.squeeze(np.argwhere(payoff == envelope)), tau_max

    def find_replicating_strategy(self):
        # matrix of differences between higher and lower price at certain time
        divisor = -np.diff(self.put_prices_tree.tree[:, 1:], axis=0)
        # fill redundant entries with ones to avoid division by 0
        divisor[np.tril_indices(divisor.shape[0], -1)] = 1
        # calculate ksi_0
        ksi_0 = np.array([self._cross_diff(U[i:i + 2], X[i:i + 2])
                          for U, X in zip(self.envelope_tree[:, 1:].T, self.put_prices_tree.tree[:, 1:].T)
                          for i in range(len(U) - 1)])
        ksi_0 = ksi_0.reshape(self.put_prices_tree.tree[1:, 1:].shape).T / divisor
        # calculate ksi_1
        ksi_1 = -np.diff(self.envelope_tree[:, 1:], axis=0) / divisor
        return ksi_0, ksi_1

    @staticmethod
    def _cross_diff(u, x):
        return u[1] * x[0] - u[0] * x[1]


def european_discount(func):
    @functools.wraps(func)
    def wrapper_european_discount(asset_price, **option_params):
        # strike is  the only obligatory keyword argument
        option_params['strike'] /= np.exp(option_params['rate'] * (asset_price.shape[0] - 1))
        return func(asset_price, **option_params)

    return wrapper_european_discount


def american_discount(func):
    @functools.wraps(func)
    def wrapper_american_discount(asset_price, **option_params):
        # strike is  the only obligatory keyword argument
        size = asset_price.shape[0]
        option_params['strike'] = option_params['strike'] / np.exp(
            option_params['rate'] * np.array([np.arange(size), ] * size))
        return func(asset_price, **option_params)

    return wrapper_american_discount


# All payoff functions must be supplied with additional argument **kwargs. It allows the BinomialTree class to supply
# payoff function with interest rate needed for strike discounting, which is handled by decorators.

@european_discount
def european_call(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[:, -1] = np.maximum(asset_price[:, -1] - strike, 0)
    return payoff_tree


@european_discount
def european_put(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[:, -1] = np.maximum(strike - asset_price[:, -1], 0)
    return payoff_tree


@american_discount
def american_call(asset_price, strike, **kwargs):
    return np.maximum(asset_price - strike, 0)


@american_discount
def american_put(asset_price, strike, **kwargs):
    return np.maximum(strike - asset_price, 0)


@american_discount
def bermuda_call(asset_price, strike, bermuda_freq, **kwargs):
    freq_seq = [t for t in range(bermuda_freq, asset_price.shape[1], bermuda_freq)]
    if freq_seq[-1] != asset_price.shape[1] - 1:
        freq_seq.append(asset_price.shape[1] - 1)
    zeros_ids = np.delete(np.arange(asset_price.shape[1]), freq_seq)
    payoff_tree = np.maximum(asset_price - strike, 0)
    payoff_tree[:, zeros_ids] = 0
    return payoff_tree


@american_discount
def bermuda_put(asset_price, strike, bermuda_freq, **kwargs):
    freq_seq = [t for t in range(bermuda_freq, asset_price.shape[1], bermuda_freq)]
    if freq_seq[-1] != asset_price.shape[1] - 1:
        freq_seq.append(asset_price.shape[1] - 1)
    zeros_ids = np.delete(np.arange(asset_price.shape[1]), freq_seq)
    payoff_tree = np.maximum(strike - asset_price, 0)
    payoff_tree[:, zeros_ids] = 0
    return payoff_tree


@european_discount
def european_binary_call(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    (payoff_tree[:, -1])[asset_price[:, -1] >= strike] = 1
    return payoff_tree


@european_discount
def european_binary_put(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    (payoff_tree[:, -1])[asset_price[:, -1] <= strike] = 1
    return payoff_tree


@american_discount
def american_binary_call(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[asset_price >= strike] = 1
    return payoff_tree


@american_discount
def american_binary_put(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    payoff_tree[asset_price <= strike] = 1
    return payoff_tree


@european_discount
def european_asset_or_nothing_call(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    positive_payoff = (asset_price[:, -1])[asset_price[:, -1] >= strike]
    (payoff_tree[:, -1])[asset_price[:, -1] >= strike] = positive_payoff
    return payoff_tree


@european_discount
def european_asset_or_nothing_put(asset_price, strike, **kwargs):
    payoff_tree = np.zeros_like(asset_price)
    positive_payoff = (asset_price[:, -1])[asset_price[:, -1] <= strike]
    (payoff_tree[:, -1])[asset_price[:, -1] <= strike] = positive_payoff
    return payoff_tree


@american_discount
def american_asset_or_nothing_call(asset_price, strike, **kwargs):
    payoff_tree = np.copy(asset_price)
    payoff_tree[payoff_tree < strike] = 0
    return payoff_tree


@american_discount
def american_asset_or_nothing_put(asset_price, strike, **kwargs):
    payoff_tree = np.copy(asset_price)
    payoff_tree[payoff_tree > strike] = 0
    return payoff_tree
