import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output, State
from icecream import ic

import default_params
import layout
import params_labels
import utils
from src.binomial_tree import BinomialTree
from src.options import Analyzer
from src.options import american_put

# import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

binomial_tree = None
option_analyzer = None

app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                html.B('Stock'),
                html.Br(),
                dcc.Dropdown(
                    id='stock-dropdown',
                    **layout.stock_dropdown
                )
            ], style={'display': 'inline-block'}),

            html.P(),

            html.Div([
                html.B('Number of Trading Days'),
                html.Br(),
                dcc.Input(
                    id='trading-days-input',
                    **layout.trading_days_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Drift'),
                html.Br(),
                dcc.Input(
                    id='drift-input',
                    **layout.drift_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Volatility'),
                html.Br(),
                dcc.Input(
                    id='vol-input',
                    **layout.vol_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Risk-Free Interest Rate'),
                html.Br(),
                dcc.Input(
                    id='rate-input',
                    **layout.rate_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Initial Price'),
                html.Br(),
                dcc.Input(
                    id='price-input',
                    **layout.price_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.P(),

            html.Button(
                id='submit-stock-button',
                **layout.submit_stock_button
            ),

            html.Div(id='current-stock-container')

        ], style={'display': 'block', 'margin-left': '1vw'}),

        html.Hr(),

        html.Div([

            html.P(),

            html.Div([
                html.B('Option Type'),
                html.Br(),
                dcc.Dropdown(
                    id='option-type-dropdown',
                    **layout.option_type_dropdown
                )
            ]),

            html.P(),

            html.Div([
                dcc.RadioItems(
                    id='call-put-radio',
                    **layout.call_put_radio
                )
            ]),

            html.P(),

            html.Div([
                html.B('Strike'),
                html.Br(),
                dcc.Input(
                    id='strike-input',
                    **layout.strike_input
                )
            ], style={'display': 'inline-block'}),

            html.Div([
                html.B('Maturity'),
                html.Br(),
                dcc.Input(
                    id='maturity-input',
                    **layout.maturity_input
                )
            ], style={'display': 'inline-block'}),

            html.P(),

            html.Div([
                html.B('Upper Barrier'),
                html.Br(),
                dcc.Input(
                    id='up-bar-input',
                    **layout.up_bar_input
                )
            ], style={'display': 'inline-block'}),

            html.Div([
                dcc.RadioItems(
                    id='up-bar-radio',
                    **layout.up_bar_radio
                ),
            ], style={'display': 'inline-block'}),

            html.P(),

            html.Div([
                html.B('Lower Barrier'),
                html.Br(),
                dcc.Input(
                    id='low-bar-input',
                    **layout.low_bar_input
                )
            ], style={'display': 'inline-block'}),

            html.Div([
                dcc.RadioItems(
                    id='low-bar-radio',
                    **layout.low_bar_radio
                )
            ], style={'display': 'inline-block'}),

            html.P(),

            html.Button(
                id='submit-option-button',
                **layout.submit_option_button
            ),

            html.P(),

            html.Div(id='current-option-container'),

            html.Hr(),

            html.Button(
                id='generate-button',
                **layout.generate_button
            ),

        ], style={'display': 'block', 'margin-left': '1vw'}),

        html.P(),

        html.Div([
            cyto.Cytoscape(
                id='tree-plot',
                **layout.tree_plot
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            dcc.Markdown(
                id='selected-prices-md'
            )
        ], style={'display': 'inline-block', 'vertical-align': 'top'})
    ])
])


@app.callback(
    Output('vol-input', 'value'),
    Output('drift-input', 'value'),
    Output('price-input', 'value'),
    Input('stock-dropdown', 'value')
)
def set_stock_defaults(stock):
    return default_params.vol[stock], \
           default_params.drift[stock], \
           default_params.price[stock]


@app.callback(
    Output('maturity-input', 'max'),
    Output('maturity-input', 'value'),
    Input('trading-days-input', 'value')
)
def set_maturity_defaults(trading_days):
    return trading_days, trading_days


@app.callback(
    Output('strike-input', 'value'),
    Input('price-input', 'value')
)
def set_strike_defaults(init_price):
    return init_price


@app.callback(
    Output('submit-stock-button', 'disabled'),
    Output('submit-stock-button', 'style'),
    Input('stock-dropdown', 'value'),
    Input('rate-input', 'value'),
    Input('vol-input', 'value'),
    Input('drift-input', 'value'),
    Input('trading-days-input', 'value'),
    Input('price-input', 'value')
)
def enable_stock_submission(*stock_params):
    border_style = '2px solid '
    value_is_missing = any((param is None for param in stock_params))
    if value_is_missing:
        is_disabled = True
        border_style += 'red'
    else:
        is_disabled = False
        border_style += 'green'
    return is_disabled, {'border': border_style}


@app.callback(
    Output('submit-option-button', 'disabled'),
    Output('submit-option-button', 'style'),
    Input('option-type-dropdown', 'value'),
    Input('strike-input', 'value'),
    Input('maturity-input', 'value'),
    Input('up-bar-input', 'value'),
    Input('low-bar-input', 'value')
)
def enable_option_submission(*option_params):
    border_style = '2px solid '
    # We allow barriers to be not specified
    value_is_missing = any((param is None for param in option_params[:-2]))
    if value_is_missing:
        is_disabled = True
        border_style += 'red'
    else:
        is_disabled = False
        border_style += 'green'
    return is_disabled, {'border': border_style}


@app.callback(
    Output('current-stock-container', 'children'),
    Input('submit-stock-button', 'n_clicks'),
    State('stock-dropdown', 'value'),
    State('trading-days-input', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    prevent_initial_call=True
)
def submit_stock_params(stock_btn, *states):
    return utils.generate_table_content(params_labels.stock, states)


@app.callback(
    Output('current-option-container', 'children'),
    Input('submit-option-button', 'n_clicks'),
    State('option-type-dropdown', 'value'),
    State('call-put-radio', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value'),
    State('up-bar-input', 'value'),
    State('up-bar-radio', 'value'),
    State('low-bar-input', 'value'),
    State('low-bar-radio', 'value'),
    prevent_initial_call=True
)
def submit_option_params(option_btn, *states):
    return utils.generate_table_content(params_labels.option, states)


@app.callback(
    Output('generate-button', 'disabled'),
    Output('generate-button', 'style'),
    Input('submit-stock-button', 'n_clicks'),
    Input('submit-option-button', 'n_clicks')
)
def enable_generate_button(stock_btn, option_btn):
    border_style = '2px solid '
    if stock_btn > 0 and option_btn > 0:
        is_disabled = False
        border_style += 'green'
    else:
        is_disabled = True
        border_style += 'red'
    return is_disabled, {'border': border_style}


@app.callback(
    Output('tree-plot', 'elements'),
    Input('generate-button', 'n_clicks'),
    State('trading-days-input', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('call-put-radio', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value'),
    State('up-bar-input', 'value'),
    State('up-bar-radio', 'value'),
    State('low-bar-input', 'value'),
    State('low-bar-radio', 'value'),
    prevent_initial_call=True
)
def generate_data(gen_btn, nb_periods, drift, vol, rate, init_price, option, option_type, strike, maturity,
                  up_bar, up_bar_type, low_bar, low_bar_type):
    global binomial_tree
    global option_analyzer
    mean, std, rf = utils.adjust_params(drift, vol, rate)
    binomial_tree = BinomialTree(nb_periods, mean, std, rf, init_price)
    binomial_tree.generate()
    # todo: implement choice of the option (now it is always american put)
    option_analyzer = Analyzer(binomial_tree, american_put, strike=strike)
    return utils.generate_nodes(binomial_tree.tree, nb_periods)


@app.callback(
    Output('selected-prices-md', 'children'),
    Input('tree-plot', 'selectedNodeData')
)
def do_sth_with_selected_prices(data_list):
    # todo: Make this function do something useful
    if not data_list:
        return
    else:
        id_tuples = [utils.retrieve_id(data['id']) for data in data_list]
        row_ids = np.array([tup[0] for tup in id_tuples])
        col_ids = np.array([tup[1] for tup in id_tuples])
        prices_list = binomial_tree.tree[row_ids, col_ids]
        return "Chosen prices" + "\n*".join(prices_list.astype(str))


if __name__ == '__main__':
    app.run_server(debug=True)
