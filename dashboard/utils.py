import dash_html_components as html
import numpy as np
import pandas as pd
from icecream import ic
from src.options import american_put


def generate_table_content(names, values):
    """Generate HTML horizontal table for displaying submitted parameters"""
    names = html.Tr([html.Th(name) for name in names])
    content = html.Tr([html.Td(value) for value in values])
    return names, content


def adjust_params(drift, vol, rate, scale=252):
    """Calculate parameters with respect to single day"""
    return drift / scale, vol / np.sqrt(scale), rate / scale


def generate_nodes(prices, nb_periods, scale_x=50, scale_y=35):
    """Generate Cytoscape nodes"""
    positions = _generate_nodes_positions(nb_periods, scale_x, scale_y)
    layouts = _generate_nodes_layout(prices, positions, scale_x, scale_y)
    return [{'data': layout, 'position': position, 'locked': True}
            for layout, position in zip(layouts, positions)]


def _generate_nodes_positions(nb_periods, scale_x, scale_y):
    """Generate Cytoscape nodes positions (coordinates)"""
    # The strange thing is that node with y=-1 is higher than node with y=1
    positions = [{'x': scale_x * x, 'y': scale_y * y}
                 for x in range(nb_periods + 1)
                 for y in range(-x, x + 1, 2)]
    return positions


def _generate_nodes_layout(prices, positions, scale_x, scale_y):
    """Generate Cytoscape nodes layouts i.e. dictionaries for 'data' key"""
    labels = np.concatenate([prices[:(t + 1), t] for t in range(prices.shape[0])])
    return [{'id': _generate_cyto_id(position, scale_x, scale_y), 'label': round(label, 2)}
            for position, label in zip(positions, labels)]


def _generate_cyto_id(position, scale_x, scale_y):
    """Generate unique names for a node based on its position"""
    x, y = position['x'], position['y']
    x_label, y_label = str(int(x / scale_x)), str(int(y / scale_y))
    return x_label + '_' + y_label


def retrieve_id(cyto_id):
    """Retrieve indices of node's price (in tree of prices) from its cyto_id"""
    col, row = cyto_id.split('_')
    col_id = int(col)
    # Due to strange coordinates assignment I do not reverse the list before finding the index of the element
    # Previously I did list(range(-col_id, col_id + 1, 2))[::-1].index(int(row)), but it worked in wrong direction
    row_id = list(range(-col_id, col_id + 1, 2)).index(int(row))
    return row_id, col_id


def determine_payoff_func(*args):
    """Determine payoff function base on given parameters"""
    # implement this function to return different payoff functions
    return american_put


def create_plotting_df(days, stock, envelope, excess, mtg):
    return pd.DataFrame(data={
        'Day': days,
        'Stock': stock,
        'Envelope': envelope,
        'Excess': excess,
        'mtg': mtg
    })


if __name__ == '__main__':
    nodes = _generate_nodes_positions(3, 1, 1)
    print(nodes)
    ic(retrieve_id('1_-1'))
