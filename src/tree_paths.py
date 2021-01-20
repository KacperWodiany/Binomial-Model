import numpy as np


def extract(tree, path):
    try:
        # indicate when path (price of an asset) has dropped
        drops = -np.minimum(path, 0)
    except TypeError:
        # when path is passed as a dict of arrays of indices
        rows_ids, cols_ids = path['rows_ids'], path['cols_ids']
        if not _are_valid_path_ids(rows_ids, cols_ids, tree.shape[1]):
            raise ValueError('Given ids are not valid path ids')
    else:
        # get ids of rows (in tree matrix) in which prices for given omega are placed
        rows_ids = np.hstack((0, np.cumsum(drops)))
        # get ndarray of columns ids
        cols_ids = np.arange(0, tree.shape[1])
    # get values in respective rows in respective columns using numpy's advanced indexing (indexing with two ndarrays)
    return tree[rows_ids, cols_ids]


def extract_with_neighbors(tree, path):
    try:
        # indicate when path (price of an asset) has dropped
        drops = -np.minimum(path, 0)
    except TypeError:
        # when path is passed as a dict of arrays of indices
        rows_ids, cols_ids = path['rows_ids'], path['cols_ids']
        if not _are_valid_path_ids(rows_ids, cols_ids, tree.shape[1]):
            raise ValueError('Given ids are not valid path ids')
    else:
        # get ids of rows (in tree matrix) in which prices for given omega are placed
        rows_ids = np.hstack((0, np.cumsum(drops)))
        # get ndarray of columns ids
        cols_ids = np.arange(0, tree.shape[1])
    # check if price raised(0) or dropped(1) comparing to previous period
    has_dropped = np.hstack((0, np.diff(rows_ids)))
    # find ids of rows (in tree matrix) of neighbor prices
    neighbor_rows_id = [rows_ids[i] - 1 if has_dropped[i] == 1
                        else rows_ids[i] + 1
                        for i in range(1, len(rows_ids))]
    # above arrays doesn't contain id of initial asset price (at time 0)
    # We add 0 at the beginning to correctly extract path of neighbor prices
    rows_ids = np.vstack((rows_ids, np.hstack((0, neighbor_rows_id))))
    # adjust shape of columns id array, so advanced indexing with 2-D arrays can be used
    cols_ids = np.array([cols_ids, ] * 2)
    # get values in respective rows in respective columns using numpy's advanced indexing (indexing with two ndarrays)
    return tree[rows_ids, cols_ids]


def _are_valid_path_ids(row_ids, col_ids, tree_size):
    cols_check = all(np.diff(col_ids) == 1) and col_ids[0] == 0
    rows_check = all(True if diff in (0, 1) else False for diff in np.diff(row_ids))
    len_check = len(row_ids) == len(col_ids) == tree_size
    return all((rows_check, cols_check, len_check))
