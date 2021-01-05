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
        # add drift term
        self.tree = tree_gen_mx * np.exp((self.mean - self.rate) * np.arange(0, self.periods + 1))

    def _find_emm(self):
        # TODO: Take dividend yield into account
        self.q = (np.exp(self.rate - self.mean) - np.exp(-self.std)) / (np.exp(self.std) - np.exp(-self.std))

    def _generate_increments(self):
        increments = np.triu(np.ones((self.periods + 1, self.periods + 1)), k=0)
        # fill diagonal with sequence 0, -1, -2, ..., -T
        np.fill_diagonal(increments, -np.arange(0, self.periods + 1))
        # apply dividend assumption
        increments[:, self.div_periods] -= np.log(1 + self.div_yield) / self.std
        return increments

    def calculate_U(self, payoff):
        h = self._calculate_H(payoff)
        u = np.copy(h)
        # TODO: Avoid for-loop.
        for t in range(1, self.periods + 1):
            # calculate expectation of future value of Snell's Envelope - E(U_{t+1}|F_t)
            prev_u = self.q * u[:-1, -t] + (1 - self.q) * u[1:, -t]
            # fill redundant entries with 0
            u[:, -(t + 1)] = np.hstack((prev_u, 0))
        return np.maximum(u, h)

    def _calculate_H(self, payoff):
        # payoff function must handle 2-D array
        return payoff(self.tree)

    def get_prices(self, omega):
        return tree_paths.extract(self.tree, omega)
