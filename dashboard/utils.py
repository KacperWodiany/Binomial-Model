import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from icecream import ic

from payoffs import payoff_dict
from src.binomial_tree import BinomialTree
from src.options import Analyzer


def generate_table_content(names, values):
    """Generate HTML horizontal table for displaying submitted parameters"""
    names = html.Tr([html.Th(name) for name in names])
    content = html.Tr([html.Td(value) for value in values])
    return names, content


def generate_nodes(drift, init_price, maturity, rate, vol, div_periods, div_yield):
    """Generate Cytoscape nodes"""
    # todo: eventually scale dividend yields
    mean, std, rf = adjust_params(drift, vol, rate)
    binomial_tree = BinomialTree(maturity, mean, std, rf, init_price, div_periods=div_periods, div_yield=div_yield)
    binomial_tree.generate()
    return _generate_nodes_data(binomial_tree.tree, maturity)


def adjust_params(drift, vol, rate, scale=252):
    """Calculate parameters with respect to single day"""
    # todo: if dividend_yield will be scaled, implement scaling here, and change code below the rest of todos
    return drift / scale, vol / np.sqrt(scale), rate / scale


def _generate_nodes_data(prices, nb_periods, scale_x=50, scale_y=35):
    """Create data for generating Cytoscape nodes"""
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


def create_dividend_arrays(dividend_freq, dividend_yield, nb_periods):
    """Create array of periods when dividend is paid"""
    if dividend_freq == 0:
        dividend_periods = 0
        dividend_yields = 0
    else:
        dividend_periods = np.arange(dividend_freq, nb_periods+1, dividend_freq)
        dividend_yields = dividend_yield * np.ones_like(dividend_periods)
    return dividend_periods, dividend_yields


def create_endpoint_path(rows_ids, cols_ids, tree_size):
    """Create path from given endpoints"""
    if not _is_valid_endpoint(rows_ids, cols_ids, tree_size):
        raise ValueError('Given ids are not valid endpoints ids')
    downs = [(x, x) for x in range(rows_ids[0] + 1)]
    ups = [(rows_ids[0], x + 1) for x in range(rows_ids[0], tree_size - 1)]
    path_rows, path_cols = map(list, zip(*(downs + ups)))
    return {'rows_ids': path_rows, 'cols_ids': path_cols}


def _is_valid_endpoint(rows_ids, cols_ids, tree_size):
    """Check if given ids are valid endpoints ids"""
    is_single = len(rows_ids) == len(cols_ids) == 1
    row_id, col_id = rows_ids[0], cols_ids[0]
    col_id_check = col_id == tree_size - 1
    row_id_check = 0 <= row_id <= tree_size - 1
    return all((is_single, row_id_check, col_id_check))


def submit_path(path_btn, selected_nodes, drift, vol, rate, init_price,
                option, bermuda, option_type, strike, maturity, div_periods, div_yield):
    """Perform calculations and draw line plots (when whole path was submitted)"""
    excess_graph, envelope_graph = None, None
    try:
        # if selected_nodes is not none
        ids = [retrieve_id(node['id']) for node in selected_nodes]
    except TypeError:
        submission_msg = 'No prices submitted' if path_btn > 0 else None
    else:
        # sort in case nodes weren't selected in order
        ids.sort(key=lambda item: item[1])
        try:
            # if selected_nodes was not an empty list
            rows_ids, cols_ids = map(list, zip(*ids))
        except ValueError:
            submission_msg = 'No prices submitted' if path_btn > 0 else None
        else:
            path = {'rows_ids': rows_ids, 'cols_ids': cols_ids}

            # todo: eventually scale dividend yield
            mean, std, rf = adjust_params(drift, vol, rate)
            binomial_tree = BinomialTree(maturity, mean, std, rf, init_price,
                                         div_periods=div_periods, div_yield=div_yield)
            binomial_tree.generate()
            payoff_func = determine_payoff_func(option, option_type)
            option_analyzer = Analyzer(binomial_tree, payoff_func, strike=strike, bermuda_freq=bermuda)

            try:
                # if path with given ids can be extracted
                mtg, excess, envelope = option_analyzer.decompose_envelope(path, True)
            except ValueError:
                submission_msg = "Submitted prices don't create proper path"
            else:
                submission_msg = "Path submitted successfully"

                stock = binomial_tree.get_prices(path)
                stopping_times, tau_max = option_analyzer.find_stopping_times(path)
                df = create_plotting_df(cols_ids, stock, envelope, excess, mtg,
                                        stopping_times, tau_max, option, bermuda)

                envelope_fig, excess_fig = _create_figures(df)

                envelope_graph, excess_graph = _create_graphs(envelope_fig, excess_fig)

    return submission_msg, excess_graph, envelope_graph


def determine_payoff_func(option, option_type):
    """Determine payoff function base on given parameters"""
    try:
        payoff = payoff_dict[option][option_type]
    except KeyError:
        print('Given option was not found in the dictionary. American Put payoff is returned')
        payoff = payoff_dict['American']["put"]

    return payoff


def create_plotting_df(days, stock, envelope, excess, mtg, stopping_times, tau_max, option, bermuda_freq):
    """Create data frame for plotting"""
    if option == 'European':
        df = pd.DataFrame(data={
            'Day': days,
            'Stock': stock,
            'Envelope': envelope,
            'Excess': excess,
            'mtg': mtg
        })
    elif option == 'Bermuda':
        tau = ['Yes' if t in stopping_times else 'No' for t in days]
        tau[tau_max] = 'Largest Optimal'
        freq_seq = [t for t in range(bermuda_freq, len(days), bermuda_freq)]
        if freq_seq[-1] != len(days) - 1:
            freq_seq.append(len(days) - 1)
        df = pd.DataFrame(data={
            'Day': days,
            'Stock': stock,
            'Envelope': envelope,
            'Excess': excess,
            'mtg': mtg,
            'Stopping Time': [tau[i] if i in freq_seq else 'Not Applicable' for i in range(len(tau))]
        })
    else:
        tau = ['Yes' if t in stopping_times else 'No' for t in days]
        tau[tau_max] = 'Largest Optimal'
        df = pd.DataFrame(data={
            'Day': days,
            'Stock': stock,
            'Envelope': envelope,
            'Excess': excess,
            'mtg': mtg,
            'Stopping Time': tau
        })
    return df


def _create_figures(df):
    """Create plots (figures)"""
    try:
        excess_fig = px.scatter(df, x='Day', y='Excess', color='Stopping Time', width=800, height=400)
        envelope_fig = px.scatter(df, x='Day', y='Envelope', color='Stopping Time', width=800, height=400)
    except ValueError:
        excess_fig = None  # px.line(df, x='Day', y='Excess', width=800, height=400)
        envelope_fig = px.line(df, x='Day', y='Envelope', width=800, height=400)
    else:
        excess_fig_line = px.line(df, x='Day', y='Excess', width=800, height=400)
        envelope_fig_line = px.line(df, x='Day', y='Envelope', width=800, height=400)
        excess_fig.update_traces(marker=dict(size=10,
                                             line=dict(width=2,
                                                       color='DarkSlateGrey')),
                                 selector=dict(mode='markers'))
        envelope_fig.update_traces(marker=dict(size=10,
                                               line=dict(width=2,
                                                         color='DarkSlateGrey')),
                                   selector=dict(mode='markers'))
        excess_fig.add_trace(excess_fig_line.data[0])
        envelope_fig.add_trace(envelope_fig_line.data[0])
    return envelope_fig, excess_fig


def _create_graphs(envelope_fig, excess_fig):
    """Create graph objects (dash core components)"""
    if excess_fig is None:
        excess_graph = None
    else:
        excess_graph = dcc.Graph(id='excess-plot', figure=excess_fig)
    envelope_graph = dcc.Graph(id='envelope-plot', figure=envelope_fig)
    return envelope_graph, excess_graph


def submit_endpoints(endpoints_btn, selected_nodes, drift, vol, rate, init_price,
                     option, bermuda, option_type, strike, maturity, div_periods, div_yield):
    """Perform calculations and draw line plots (when endpoint was submitted)"""
    excess_graph, envelope_graph = None, None
    edges_id = None
    try:
        # if selected_nodes is not none
        ids = [retrieve_id(node['id']) for node in selected_nodes]
    except TypeError:
        submission_msg = 'No endpoint submitted' if endpoints_btn > 0 else None
    else:
        # sort in case nodes weren't selected in order
        ids.sort(key=lambda item: item[1])
        try:
            # if selected_nodes is not an empty list
            rows_ids, cols_ids = map(list, zip(*ids))
        except ValueError:
            submission_msg = 'No endpoint submitted' if endpoints_btn > 0 else None
        else:
            try:
                path = create_endpoint_path(rows_ids, cols_ids, maturity + 1)
            except ValueError:
                submission_msg = "Submitted price is not proper endpoint"
            else:
                submission_msg = "Endpoint submitted successfully"
                # Path was created successfully so I trust rows_ids is one element list with proper value
                edges_id = rows_ids[0]

                # todo: eventually scale dividend yield
                mean, std, rf = adjust_params(drift, vol, rate)
                binomial_tree = BinomialTree(maturity, mean, std, rf, init_price,
                                             div_periods=div_periods, div_yield=div_yield)
                binomial_tree.generate()
                payoff_func = determine_payoff_func(option, option_type)
                option_analyzer = Analyzer(binomial_tree, payoff_func, strike=strike, bermuda_freq=bermuda)

                mtg, excess, envelope = option_analyzer.decompose_envelope(path, all_processes=True)
                stock = binomial_tree.get_prices(path)
                stopping_times, tau_max = option_analyzer.find_stopping_times(path)
                df = create_plotting_df(np.arange(0, maturity + 1), stock, envelope, excess, mtg,
                                        stopping_times, tau_max, option, bermuda)

                envelope_fig, excess_fig = _create_figures(df)

                envelope_graph, excess_graph = _create_graphs(envelope_fig, excess_fig)

    return submission_msg, excess_graph, envelope_graph, edges_id


def create_endpoint_path_markers(row_id, tree_size):
    """Generate edges to mark the path indicated by endpoint"""
    ends_down = tuple(str(i) + '_' + str(i) for i in range(row_id + 1))
    ends_up = tuple(str(row_id + i) + '_' + str(row_id - i) for i in range(1, tree_size - row_id + 1))
    ends = ends_down + ends_up
    return [{'data': {'source': start, 'target': end}} for start, end in zip(ends[:-1], ends[1:])]
