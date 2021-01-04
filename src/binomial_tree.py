import numpy as np
import tree_paths


# Works fine for path independent options (European, Bermuda, American)
class BinomialTree:

    def __init__(self, t, s, m, r, x0, num0):
        self.t = t
        self.s = s
        self.m = m
        self.r = r
        self.x0 = x0
        self.num0 = num0
        self.q = (np.exp(r - s) - np.exp(-m)) / (np.exp(m) - np.exp(-m))
        self.tree = None

    def generate(self):
        # create matrix of increments from which the tree matrix will be generated
        tree_gen_mx = np.triu(np.ones((self.t + 1, self.t + 1)), k=0)
        # fill diagonal with sequence 0, -1, -2, ..., -T
        np.fill_diagonal(tree_gen_mx, -np.arange(0, self.t + 1))
        # calculate tree of discounted prices
        tree_gen_mx = np.cumsum((self.s - self.r) + self.m * tree_gen_mx, axis=1)
        self.tree = self.x0 / self.num0 * np.exp(tree_gen_mx)

    def calculate_H(self, payoff):
        # payoff function must handle 2-D array
        return payoff(self.tree)

    def calculate_U(self, payoff):
        h = self.calculate_H(payoff)
        u = np.copy(h)
        # TODO: Avoid for-loop.
        for t in range(1, self.t + 1):
            # calculate expectation of future value of Snell's Envelope - E(U_{t+1}|F_t)
            prev_u = self.q * u[:-1, -t] + (1 - self.q) * u[1:, -t]
            # fill redundant entries with 0
            u[:, -(t + 1)] = np.hstack((prev_u, 0))
        return np.maximum(u, h)

    def get_prices(self, omega):
        return tree_paths.extract(self.tree, omega)
