import numpy as np


def extract(tree, omega):
    # indicate when path (price of an asset) has dropped
    drops = -np.minimum(omega, 0)
    # get ids of rows (in tree matrix) in which prices for given omega are placed
    rows_id = np.hstack((0, np.cumsum(drops)))
    # get ndarray of columns ids
    cols_id = np.arange(0, tree.shape[1])
    # get values in respective rows in respective columns using numpy's advanced indexing (indexing with two ndarrays)
    return tree[rows_id, cols_id]


def extract_with_neighbors(tree, omega):
    # indicate when path (price of an asset) has dropped
    drops = -np.minimum(omega, 0)
    # get ids of rows (in tree matrix) in which prices for given omega are placed
    rows_id = np.hstack((0, np.cumsum(drops)))
    # get ndarray of columns ids
    cols_id = np.arange(0, tree.shape[1])
    # check if price raised(0) or dropped(1) comparing to previous period
    has_dropped = np.hstack((0, np.diff(rows_id)))
    # find ids of rows (in tree matrix) of neighbor prices
    neighbor_rows_id = [rows_id[i] - 1 if has_dropped[i] == 1
                        else rows_id[i] + 1
                        for i in range(1, len(rows_id))]
    # above arrays doesn't contain id of initial asset price (at time 0)
    # We add 0 at the beginning to correctly extract path of neighbor prices
    rows_id = np.vstack((rows_id, np.hstack((0, neighbor_rows_id))))
    # adjust shape of columns id array, so advanced indexing with 2-D arrays can be used
    cols_id = np.array([cols_id, ] * 2)
    # get values in respective rows in respective columns using numpy's advanced indexing (indexing with two ndarrays)
    return tree[rows_id, cols_id]
