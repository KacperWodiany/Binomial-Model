import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State

import default_params
import layout
import params_labels
import utils
from src.binomial_tree import BinomialTree
from src.options import Analyzer

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Option Type'),
                html.Br(),
                dcc.Dropdown(
                    id='option-type-dropdown',
                    **layout.option_type_dropdown
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div(id='bermuda-seasons-dropdown-container', children=[
                html.B('Bermuda seasons'),
                html.Br(),
                dcc.Dropdown(
                    id='bermuda-seasons-dropdown',
                    **layout.bermuda_seasons_dropdown
                )
            ], style={'display': 'none', 'margin-right': '1vw'}),

            html.Div([
                html.Br(),
                dcc.Dropdown(
                    id='call-put-dropdown',
                    **layout.call_put_dropdown
                )
            ], style={'display': 'inline-block'}),

            html.P(),

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

            html.Div([
                html.B('Strike'),
                html.Br(),
                dcc.Input(
                    id='strike-input',
                    **layout.strike_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'}),

            html.Div([
                html.B('Maturity'),
                html.Br(),
                dcc.Input(
                    id='maturity-input',
                    **layout.maturity_input
                )
            ], style={'display': 'inline-block', 'margin-right': '1vw'})

        ], style={'display': 'block', 'margin-left': '1vw'}),

        html.Div(id='current-stock-container', style={'display': 'block', 'margin-left': '1vw'}),

        html.Div(id='current-option-container', style={'display': 'block', 'margin-left': '1vw'}),

        html.Hr(),

        html.Button(
            id='generate-button',
            **layout.generate_button
        )
    ]),

    html.P(),

    html.Div([
        cyto.Cytoscape(
            id='tree-plot',
            **layout.tree_plot
        )
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Div([
            html.Button(
                id='select-path-button',
                **layout.select_path_button
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B(
                id='selected-price-msg'
            )
        ], style={'display': 'inline-block', 'margin-left': '3vw'}),

        html.Div(
            id='excess-plot-container'
        ),

        html.Div(
            id='envelope-plot-container'
        )
    ], style={'display': 'inline-block', 'vertical-align': 'top'})
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
    Output('strike-input', 'value'),
    Input('price-input', 'value')
)
def set_strike_defaults(init_price):
    return init_price


@app.callback(
    Output('generate-button', 'disabled'),
    Output('generate-button', 'style'),
    Input('stock-dropdown', 'value'),
    Input('drift-input', 'value'),
    Input('vol-input', 'value'),
    Input('rate-input', 'value'),
    Input('price-input', 'value'),
    Input('option-type-dropdown', 'value'),
    Input('call-put-dropdown', 'value'),
    Input('strike-input', 'value'),
    Input('maturity-input', 'value')
)
def enable_generate_button(*params):
    border_style = '2px solid '
    value_is_missing = any((param is None for param in params))
    if value_is_missing:
        is_disabled = True
        border_style += 'red'
    else:
        is_disabled = False
        border_style += 'green'
    return is_disabled, {'border': border_style}


@app.callback(
    Output('current-stock-container', 'children'),
    Output('current-option-container', 'children'),
    Input('generate-button', 'n_clicks'),
    State('bermuda-seasons-dropdown-container', 'style'),
    State('stock-dropdown', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('bermuda-seasons-dropdown', 'value'),
    State('call-put-dropdown', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value')
)
def display_current_parameters(gen_btn, bermuda_style, *params):
    stock_params_names = params_labels.stock
    stock_params = params[:len(stock_params_names)]
    option_params = params[len(stock_params_names):]
    if bermuda_style['display'] == 'none':
        option_params = [option_params[i] for i in range(len(option_params)) if i != 1]
        option_params_names = params_labels.option
        option_params_names = [option_params_names[i] for i in range(len(option_params_names)) if i != 1]
    else:
        option_params_names = params_labels.option
    if gen_btn > 0:
        stock_table = utils.generate_table_content(stock_params_names, stock_params)
        option_table = utils.generate_table_content(option_params_names, option_params)
    else:
        stock_table = None
        option_table = None

    return stock_table, option_table


@app.callback(
    Output('tree-plot', 'elements'),
    Output('select-path-button', 'style'),
    Input('generate-button', 'n_clicks'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    State('maturity-input', 'value'),
    prevent_initial_call=True
)
def generate_tree_plot(gen_btn, drift, vol, rate, init_price, nb_periods):
    mean, std, rf = utils.adjust_params(drift, vol, rate)
    binomial_tree = BinomialTree(nb_periods, mean, std, rf, init_price)
    binomial_tree.generate()
    return utils.generate_nodes(binomial_tree.tree, nb_periods), {'border': '2px solid green'}


@app.callback(
    Output('selected-price-msg', 'children'),
    Output('excess-plot-container', 'children'),
    Output('envelope-plot-container', 'children'),
    Input('select-path-button', 'n_clicks'),
    State('tree-plot', 'selectedNodeData'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('bermuda-seasons-dropdown', 'value'),
    State('call-put-dropdown', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value'),
    prevent_inital_call=True
)
def select_path_and_draw_plots(select_btn, selected_nodes, drift, vol, rate, init_price,
                               option, bermuda, option_type, strike, maturity):
    excess_graph, envelope_graph = None, None
    try:
        ids = [utils.retrieve_id(node['id']) for node in selected_nodes]
    except TypeError:
        selection_msg = 'No prices selected' if select_btn > 0 else None
    else:
        # sort in case nodes weren't selected in order
        ids.sort(key=lambda item: item[1])
        try:
            rows_ids, cols_ids = map(list, zip(*ids))
        except ValueError:
            selection_msg = 'No prices selected' if select_btn > 0 else None
        else:
            # todo: clean this block of code
            path = {'rows_ids': rows_ids, 'cols_ids': cols_ids}
            mean, std, rf = utils.adjust_params(drift, vol, rate)
            binomial_tree = BinomialTree(maturity, mean, std, rf, init_price)
            binomial_tree.generate()
            # for now it is always american put
            payoff_func = utils.determine_payoff_func(option, option_type, maturity, bermuda)
            option_analyzer = Analyzer(binomial_tree, payoff_func, strike=strike)
            try:
                mtg, excess, envelope = option_analyzer.decompose_envelope(path, True)
            except ValueError:
                selection_msg = "Selected prices don't create proper path"
            else:
                selection_msg = "Path selected successfully"
                stock = binomial_tree.get_prices(path)
                df = utils.create_plotting_df(cols_ids, stock, envelope, excess, mtg)
                excess_fig = px.bar(df, x='Day', y='Excess', width=600, height=400)
                envelope_fig = px.bar(df, x='Day', y='Envelope', width=600, height=400)
                excess_graph = dcc.Graph(id='excess-plot', figure=excess_fig)
                envelope_graph = dcc.Graph(id='envelope-plot', figure=envelope_fig)
    return selection_msg, excess_graph, envelope_graph


if __name__ == '__main__':
    app.run_server(debug=True)
