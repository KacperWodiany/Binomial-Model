import numpy as np
import tree_paths


# Works fine for path independent options (European, Bermuda, American)
class BinomialTree:

    def __init__(self, periods, mean, std, rate, s0, num0=1, div_yield=0, div_periods=0):
        self.periods = periods
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
        # tree_gen_mx[:, self.div_periods] = tree_gen_mx[:, self.div_periods] / div_yield_seq
        tree_gen_mx /= div_yield_seq
        # add drift term and assign attribute
        self.tree = tree_gen_mx * np.exp((self.mean - self.rate) * np.arange(0, self.periods + 1))

    def _find_emm(self):
        # Create vector of dividend yields
        # Set 0 if no dividend assumed for the period
        dividends = np.zeros(self.periods + 1)
        # Set relevant value from div_yield if dividend is assumed
        dividends[self.div_periods] = self.div_yield
        # Calculate probability based taking dividends into account
        self.q = self._find_probability(dividends=dividends[1:])

    def _find_probability(self, dividends):
        return ((np.exp(self.rate + np.log(1 + dividends) - self.mean) - np.exp(-self.std))
                / (2 * np.sinh(self.std)))

    def _generate_increments(self):
        increments = np.triu(np.ones((self.periods + 1, self.periods + 1)), k=0)
        # fill diagonal with sequence 0, -1, -2, ..., -T
        np.fill_diagonal(increments, -np.arange(0, self.periods + 1))
        return increments

    def _create_dividend_yield_seq(self):
        # If no dividend assumed sequence consists of ones
        dividend_seq = np.ones(self.periods + 1)
        try:
            # When arrays of dividend periods and yields are passed, the array above must have products of consecutive
            # yields on respective places
            for t, d in zip(self.div_periods, self.div_yield):
                dividend_seq[t:] *= (1 + d)
        except TypeError:
            # If dividend periods are ints, we cannot iterate over them
            dividend_seq[self.div_periods:] *= (1 + self.div_yield)
        else:
            # If tree is sliced with array the sequence needs to be 2-D
            dividend_seq = np.array([dividend_seq, ] * (self.periods + 1))
        return dividend_seq

    def calculate_U(self, payoff):
        h = self._calculate_H(payoff)
        u = np.copy(h)
        for t in range(1, self.periods + 1):
            # calculate expectation of future value of Snell's Envelope - E(U_{t+1}|F_t)
            prev_u = self.q[-t + 1] * u[:-1, -t] + (1 - self.q[-t + 1]) * u[1:, -t]
            # fill redundant entries with 0
            u[:, -(t + 1)] = np.hstack((prev_u, 0))
        return np.maximum(u, h)

    def _calculate_H(self, payoff):
        # payoff function must handle 2-D array
        return payoff(self.tree)

    def calculate_expectation(self, omega, periods=None, tree=None):
        if tree is None:
            tree = self.tree
        if periods is None:
            periods = np.arange(self.periods + 1)
        # Get path and its neighbors values for given periods
        path = tree_paths.extract_with_neighbors(tree, omega)[:, periods]
        # Put greater values in upper row and smaller values in lower row
        path = -np.sort(-path[:, 1:], axis=0)
        # Arrange matrix of probabilities
        probabilities = np.array([self.q, 1 - self.q])
        return np.sum(probabilities * path, axis=0)
