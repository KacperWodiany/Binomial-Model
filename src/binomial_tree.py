import numpy as np
import tree_paths

from icecream import ic


# Works fine for path independent options (European, Bermuda, American)
class BinomialTree:

    def __init__(self, nb_periods, mean, std, rate, s0, num0=1, div_yield=0, div_periods=0):
        self.nb_periods = nb_periods
        self.mean = mean
        self.std = std
        self.rate = rate
        self.s0 = s0
        self.num0 = num0
        # If dividend is not introduced setting both values to 0 don't hurt results nor performance
        self.div_yield = div_yield
        self.div_periods = div_periods
        self.q = None
        self.tree = None

    def generate(self):
        self._find_emm()
        tree_gen_mx = self._generate_increments()
        # calculate tree of discounted prices
        # drift term is excluded from cumulative summing to prevent adding it to initial price
        tree_gen_mx = np.cumsum(self.std * tree_gen_mx, axis=1)
        tree_gen_mx = self.s0 / self.num0 * np.exp(tree_gen_mx)
        # apply dividend assumption
        div_yield_seq = self._create_dividend_yield_seq()
        tree_gen_mx /= div_yield_seq
        # add drift term and assign attribute
        self.tree = tree_gen_mx * np.exp((self.mean - self.rate) * np.arange(0, self.nb_periods + 1))

    def _find_emm(self):
        # Create vector of dividend yields
        # Set 0 if no dividend assumed for the period
        dividends = np.zeros(self.nb_periods + 1)
        # Set relevant value from div_yield if dividend is assumed
        dividends[self.div_periods] = self.div_yield
        # Calculate probability based taking dividends into account
        self.q = self._find_probability(dividends=dividends[1:])

    def _find_probability(self, dividends):
        return ((np.exp(self.rate + np.log(1 + dividends) - self.mean) - np.exp(-self.std))
                / (2 * np.sinh(self.std)))

    def _generate_increments(self):
        increments = np.triu(np.ones((self.nb_periods + 1, self.nb_periods + 1)), k=0)
        # fill diagonal with sequence 0, -1, -2, ..., -T
        np.fill_diagonal(increments, -np.arange(0, self.nb_periods + 1))
        return increments

    def _create_dividend_yield_seq(self):
        # If no dividend assumed sequence consists of ones
        dividend_seq = np.ones(self.nb_periods + 1)
        try:
            # When arrays of dividend periods and yields are passed, the array above must have products of consecutive
            # yields on respective places
            for t, d in zip(self.div_periods, self.div_yield):
                dividend_seq[t:] *= (1 + d)
        except TypeError:
            # If dividend periods and yields are ints, we cannot iterate over them
            dividend_seq[self.div_periods:] *= (1 + self.div_yield)

        dividend_seq = np.array([dividend_seq, ] * (self.nb_periods + 1))
        return dividend_seq

    def calculate_envelope_tree(self, payoff_tree):
        envelope_tree = np.copy(payoff_tree)
        for t in range(1, self.nb_periods + 1):
            # calculate expectation of future value of Snell's Envelope - E(U_{t+1}|F_t)
            previous = self.q[-t] * envelope_tree[:-1, -t] + (1 - self.q[-t]) * envelope_tree[1:, -t]
            # Take maximum of Ut and Ht (envelope and payoff at time t)
            # the array is 1 element shorter than expected
            # lower entries are filled with some numbers, but aren't used. No need to take care of them
            envelope_tree[:-1, -(t + 1)] = np.maximum(previous, payoff_tree[:-1, -(t + 1)])
        return envelope_tree

    def calculate_payoff_tree(self, payoff_func, **option_params):
        # payoff function must handle 2-D array
        # supply dictionary of option parameters with interest rate for strike discounting purposes
        option_params['rate'] = self.rate
        return payoff_func(self.tree, **option_params)

    def calculate_expectation(self, omega, tree=None):
        try:
            # Try to get path and its neighbors values for given periods
            path = tree_paths.extract_with_neighbors(tree, omega)
        except AttributeError:
            # Assign classes self.tree if tree wasn't passed
            tree = self.tree
            # Get path and its neighbors values for given periods
            path = tree_paths.extract_with_neighbors(tree, omega)
        else:
            # Create mask for sorting path
            mask_path = tree_paths.extract_with_neighbors(self.tree, omega)
        try:
            # try to create mask for sorting
            mask = np.argsort(-mask_path[:, 1:], axis=0)
        except NameError:
            # If path for creating mask was not extracted, just sort the path
            sorted_path = -np.sort(-path[:, 1:], axis=0)
        else:
            # if path for creating mask was extracted, sort the path with respect to order of stock prices in the tree
            sorted_path = np.take_along_axis(path[:, 1:], mask, axis=0)

        # Arrange matrix of probabilities
        probabilities = np.array([self.q, 1 - self.q])
        return np.sum(probabilities * sorted_path, axis=0)

    def get_prices(self, path):
        return tree_paths.extract(self.tree, path)


class BinomialTreeForBarrierPut(BinomialTree):

    def __init__(self, strike, barrier, nb_periods, mean, std, rate, s0, num0=1, div_yield=0, div_periods=0):
        super().__init__(nb_periods, mean, std, rate, s0, num0, div_yield, div_periods)
        self.strike = strike
        self.barrier = barrier

    def generate(self):
        super().generate()
        # filling lower boundary is redundant here, but it allows to see the tree as I see it
        self._fill_tree_boundaries(0, 3 * np.max(self.tree))

    def _fill_tree_boundaries(self, min_val, max_val):
        max_path, min_path = self._find_max_path(), self._find_min_path()
        max_drops, min_drops = -np.minimum(max_path, 0), -np.minimum(min_path, 0)
        max_rows_ids, min_rows_ids = np.hstack((0, np.cumsum(max_drops))), np.hstack((0, np.cumsum(min_drops)))
        cols_ids = np.arange(self.tree.shape[1])
        for col, max_row, min_row in zip(cols_ids, max_rows_ids, min_rows_ids):
            self.tree[:max_row, col] = max_val
            self.tree[min_row + 1:, col] = min_val

    def _find_max_path(self):
        t = np.arange(self.nb_periods + 1)
        strike_thresholds = (np.log(self.strike / self.s0)
                             - self.nb_periods * (self.mean - self.std)
                             + np.sum(np.log(1 + self.div_yield))
                             ) / (2 * self.std)
        max_path = np.ones(self.nb_periods)
        try:
            max_path[np.where(t >= strike_thresholds)[0][0]:] = -1
        except IndexError:
            pass
        return max_path.astype(int)

    def _find_min_path(self):
        t = np.arange(1, self.nb_periods + 1)
        dividends = np.zeros_like(t)
        dividends[self.div_periods] = self.div_yield
        barrier_thresholds = (np.log(self.barrier / self.s0)
                              - self.mean * t
                              + np.cumsum(np.log(1 + dividends))
                              ) / self.std
        min_path = -np.ones(self.nb_periods)
        try:
            # if there exists value under the barrier
            t_min = np.where(-t <= barrier_thresholds)[0][0]
        except IndexError:
            pass
        else:
            min_path[t_min] = 1
            # arrays are indexed from 0, thus t_min is smaller by 1 than t_min 'on paper',
            # thus we only need to add 1 not 2 as originally
            omega_sum = -t_min + 1
            for threshold, curr_t in zip(barrier_thresholds[t_min + 1:], list(range(t_min + 1, len(min_path)))):
                ic(curr_t)
                if omega_sum - 1 > threshold:
                    omega_sum -= 1
                    # min_path[curr_t] = -1
                else:
                    omega_sum += 1
                    min_path[curr_t] = 1
        return min_path.astype(int)

    def calculate_payoff_tree(self, bermuda_periods):
        discounted_strike = self.strike / np.exp(self.rate
                                                 * np.array([np.arange(self.tree.shape[0]), ] * self.tree.shape[0]))
        discounted_barrier = self.barrier / np.exp(self.rate
                                                   * np.array([np.arange(self.tree.shape[0]), ] * self.tree.shape[0]))
        zeros_ids = np.delete(np.arange(self.tree.shape[1]), bermuda_periods)
        payoff_tree = np.maximum(discounted_strike - self.tree, 0)
        payoff_tree[:, zeros_ids] = 0
        payoff_tree[self.tree <= discounted_barrier] = 0
        return payoff_tree

    def calculate_envelope_tree(self, payoff_tree):
        ic(payoff_tree.shape)
        envelope_tree = np.copy(payoff_tree)
        discounted_barrier = self.barrier / np.exp(self.rate
                                                   * np.array([np.arange(self.tree.shape[0]), ] * self.tree.shape[0]))
        for t in range(1, self.nb_periods + 1):
            # calculate expectation of future value of Snell's Envelope - E(U_{t+1}|F_t)
            previous = self.q[-t] * envelope_tree[:-1, -t] + (1 - self.q[-t]) * envelope_tree[1:, -t]
            # Take maximum of Ut and Ht (envelope and payoff at time t)
            # the array is 1 element shorter than expected
            # lower entries are filled with some numbers, but aren't used. No need to take care of them
            envelope_tree[:-1, -(t + 1)] = np.maximum(previous, payoff_tree[:-1, -(t + 1)])
            # set U=0 when values in (discounted) prices tree is below discounted barrier
            envelope_tree[:, -(t + 1)][self.tree[:, -(t + 1)] <= discounted_barrier[:, -(t + 1)]] = 0
        return envelope_tree


if __name__ == '__main__':
    number_of_periods = 252
    mu, sigma, rf = 1.1e-3, 1.21e-2, 4e-5
    init_price = 64.94
    # barrier_level, strike_level = 45, 60
    barrier_level, strike_level = 45, 60
    dividend_periods = np.array([53, 117, 181, 242])
    dividend_periods = dividend_periods[dividend_periods <= number_of_periods]
    if len(dividend_periods) == 0:
        dividend_periods = 0
        dividend_yield = 0
    else:
        dividend_yield = 1e-3 * np.array([6, 6, 7, 7])

    put_tree = BinomialTreeForBarrierPut(strike_level, barrier_level, number_of_periods, mu, sigma, rf, init_price,
                                         div_yield=dividend_yield, div_periods=dividend_periods)
    std_tree = BinomialTree(number_of_periods, mu, sigma, rf, init_price,
                            div_yield=dividend_yield, div_periods=dividend_periods)
    put_tree.generate()
    std_tree.generate()
    ic(put_tree._find_min_path())

    ic(std_tree.tree[:, -1])
    ic(put_tree.tree[:, -1])
    # bermuda = [64, 129, 192, 252]
    bermuda = [252]
    put_tree_payoff = put_tree.calculate_payoff_tree(bermuda)
    ic(put_tree_payoff)
    put_tree_envelope = put_tree.calculate_envelope_tree(put_tree_payoff)
    ic(put_tree_envelope[0, 0])
