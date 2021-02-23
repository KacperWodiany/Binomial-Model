import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
from dash.dependencies import Input, Output, State
from icecream import ic

import default_params
import heatmaps
import layout
import params_labels
import utils

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
                html.B('Dividend Frequency'),
                html.Br(),
                dcc.Dropdown(
                    id='dividend-freq-dropdown',
                    **layout.dividend_freq_dropdown
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

            html.Div(id='bermuda-freq-dropdown-container', children=[
                html.B('Bermuda Frequency'),
                html.Br(),
                dcc.Dropdown(
                    id='bermuda-freq-dropdown',
                    **layout.bermuda_freq_dropdown
                )
            ], style={'display': 'none'}),

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

            html.Div(id='dividend-yield-input-container', children=[
                html.B('Dividend Yield'),
                html.Br(),
                dcc.Input(
                    id='dividend-yield-input',
                    **layout.dividend_yield_input
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
        html.Br(),
        dcc.Dropdown(
            id='heatmap-dropdown',
            **layout.heatmap_dropdown
        )
    ]),

    html.Div(id='heatmap-container'),

    html.Div([
        cyto.Cytoscape(
            id='tree-plot',
            **layout.tree_plot
        )
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Div(
            id='edges-id-container',
            style={'display': 'none'}
        ),

        html.Div([
            html.Button(
                id='submit-path-button',
                **layout.submit_path_button
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.Button(
                id='submit-endpoints-button',
                **layout.submit_endpoints_button

            )
        ], style={'display': 'inline-block', 'margin-left': '1vw'}),

        html.P(),

        html.Div([
            html.B(
                id='submission-msg'
            )
        ]),

        html.Div(id='excess-plot-container'),

        html.Div(id='envelope-plot-container')

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
    Output('bermuda-freq-dropdown-container', 'style'),
    Output('bermuda-freq-dropdown', 'value'),
    Input('option-type-dropdown', 'value')
)
def show_bermuda_seasons_dropdown(option_type):
    if option_type == 'Bermuda':
        style = {'display': 'inline-block', 'margin-right': '1vw'}
        value = 5
    else:
        style = {'display': 'none'}
        value = None
    return style, value


@app.callback(
    Output('dividend-yield-input-container', 'style'),
    Output('dividend-yield-input', 'value'),
    Input('stock-dropdown', 'value'),
    Input('dividend-freq-dropdown', 'value')
)
def show_dividend_yield_input(stock, dividend_freq):
    if dividend_freq == 0:
        style = {'display': 'none'}
        value = 0
    else:
        style = {'display': 'inline-block', 'margin-right': '1vw'}
        value = default_params.dividend_yield[stock]

    return style, value


@app.callback(
    Output('generate-button', 'disabled'),
    Output('generate-button', 'style'),
    Input('bermuda-freq-dropdown', 'value'),
    Input('option-type-dropdown', 'value'),
    Input('stock-dropdown', 'value'),
    Input('dividend-freq-dropdown', 'value'),
    Input('drift-input', 'value'),
    Input('vol-input', 'value'),
    Input('rate-input', 'value'),
    Input('dividend-yield-input', 'value'),
    Input('price-input', 'value'),
    Input('call-put-dropdown', 'value'),
    Input('strike-input', 'value'),
    Input('maturity-input', 'value')
)
def enable_generate_button(bermuda, option, *params):
    border_style = '2px solid '
    value_is_missing = any((param is None for param in params))
    if value_is_missing or option is None:
        is_disabled = True
        border_style += 'red'
    elif option == 'Bermuda' and bermuda is None:
        is_disabled = True
        border_style += 'red'
    else:
        is_disabled = False
        border_style += 'green'
    return is_disabled, {'border': border_style}


@app.callback(
    Output('current-stock-container', 'children'),
    Output('current-option-container', 'children'),
    Output('heatmap-dropdown', 'style'),
    Output('heatmap-dropdown', 'options'),
    Input('generate-button', 'n_clicks'),
    State('bermuda-freq-dropdown-container', 'style'),
    State('stock-dropdown', 'value'),
    State('dividend-freq-dropdown', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('dividend-yield-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('bermuda-freq-dropdown', 'value'),
    State('call-put-dropdown', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value')
)
def display_current_parameters(gen_btn, bermuda_style, *params):
    stock_params_names = params_labels.stock
    stock_params = params[:len(stock_params_names)]
    option_params = params[len(stock_params_names):]
    if bermuda_style['display'] == 'none':
        # if bermuda option was not chosen, its parameters are excluded
        option_params = [option_params[i] for i in range(len(option_params)) if i != 1]
        option_params_names = params_labels.option
        option_params_names = [option_params_names[i] for i in range(len(option_params_names)) if i != 1]
    else:
        # if bermuda option was chosen all parameters are used
        option_params_names = params_labels.option
    if gen_btn > 0:
        stock_table = utils.generate_table_content(stock_params_names, stock_params)
        option_table = utils.generate_table_content(option_params_names, option_params)
        heatmap_dropdown_display = {'width': '350px'}
    else:
        stock_table = None
        option_table = None
        heatmap_dropdown_display = {'display': 'none'}
    if option_params[0] == 'European':
        options = [
            {'label': 'Stock Price', 'value': 'Stock_Price'},
            {'label': 'Payoff', 'value': 'Payoff'},
            {'label': 'Snells Envelope', 'value': 'Snell'},
            {'label': 'Cash in Trading Strategy', 'value': 'ksi_0'},
            {'label': 'Stock in Trading Strategy', 'value': 'ksi_1'},
            {'label': 'Excess Process Increment', 'value': 'Difference'}
        ]
    else:
        options = [
            {'label': 'Stock Price', 'value': 'Stock_Price'},
            {'label': 'Payoff', 'value': 'Payoff'},
            {'label': 'Snells Envelope', 'value': 'Snell'},
            {'label': 'Stopping Time', 'value': 'If_Stopping_Time'},
            {'label': 'Cash in Trading Strategy', 'value': 'ksi_0'},
            {'label': 'Stock in Trading Strategy', 'value': 'ksi_1'},
            {'label': 'Excess Process Increment', 'value': 'Difference'}
        ]

    return stock_table, option_table, heatmap_dropdown_display, options


@app.callback(
    Output('tree-plot', 'elements'),
    Output('submit-path-button', 'style'),
    Output('submit-endpoints-button', 'style'),
    Input('generate-button', 'n_clicks'),
    Input('edges-id-container', 'children'),
    State('dividend-freq-dropdown', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('dividend-yield-input', 'value'),
    State('price-input', 'value'),
    State('maturity-input', 'value'),
    prevent_initial_call=True
)
def generate_tree_plot(gen_btn, edges_container, dividend_freq, drift, vol, rate, dividend_yield, init_price, maturity):
    ctx = dash.callback_context
    div_periods, div_yield = utils.create_dividend_arrays(dividend_freq, dividend_yield, maturity)
    # since we only generate nodes here we set rate=0 to label them with undiscounted prices
    # we do not remove rate argument to not hurt other functionalities
    rate = 0
    if ctx.triggered[0]['prop_id'] == 'generate-button.n_clicks':
        # if generate button was clicked only nodes are generated
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol, div_periods, div_yield)
        btn_style = {'border': '2px solid green'}
    elif edges_container is not None:
        # if endpoint was submitted nodes and respective edges are generated
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol, div_periods, div_yield)
        tree_elements.extend(utils.create_endpoint_path_markers(edges_container, maturity))
        btn_style = {'border': '2px solid green'}
    else:
        # All other cases. This one is not hurt layout since prevent_initial_call=True
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol, div_periods, div_yield)
        btn_style = {'border': '2px solid green'}
    return tree_elements, btn_style, btn_style


@app.callback(
    Output('heatmap-container', 'children'),
    Input('generate-button', 'n_clicks'),
    Input('heatmap-dropdown', 'value'),
    State('dividend-freq-dropdown', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('dividend-yield-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('bermuda-freq-dropdown', 'value'),
    State('call-put-dropdown', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value'),
    prevent_initial_call=True
)
def generate_heatmap(gen_btn, heatmap_param, dividend_freq, drift, vol, rate, dividend_yield, init_price,
                     option, bermuda, option_type, strike, maturity):
    if heatmap_param is not None:
        div_periods, div_yield = utils.create_dividend_arrays(dividend_freq, dividend_yield, maturity)
        data = utils.generate_heatmap_data(drift, vol, rate, init_price, option, bermuda, option_type,
                                           strike, maturity, div_periods, div_yield)
        fig = heatmaps.plot_heatmap(data, heatmap_param, params_labels.heatmap_names[heatmap_param])
        graph = dcc.Graph(id='heatmap', figure=fig)
    else:
        graph = None
    return graph


@app.callback(
    Output('submission-msg', 'children'),
    Output('excess-plot-container', 'children'),
    Output('envelope-plot-container', 'children'),
    Output('edges-id-container', 'children'),
    Input('submit-path-button', 'n_clicks'),
    Input('submit-endpoints-button', 'n_clicks'),
    State('tree-plot', 'selectedNodeData'),
    State('dividend-freq-dropdown', 'value'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('dividend-yield-input', 'value'),
    State('price-input', 'value'),
    State('option-type-dropdown', 'value'),
    State('bermuda-freq-dropdown', 'value'),
    State('call-put-dropdown', 'value'),
    State('strike-input', 'value'),
    State('maturity-input', 'value'),
    prevent_initial_call=True
)
def submit_prices(path_btn, endpoints_btn, selected_nodes, dividend_freq, drift, vol, rate, dividend_yield, init_price,
                  option, bermuda, option_type, strike, maturity):
    ctx = dash.callback_context
    div_periods, div_yield = utils.create_dividend_arrays(dividend_freq, dividend_yield, maturity)
    if ctx.triggered[0]['prop_id'] == 'submit-path-button.n_clicks':
        submission_msg, excess_graph, envelope_graph = utils.submit_path(path_btn, selected_nodes,
                                                                         drift, vol, rate, init_price,
                                                                         option, bermuda, option_type, strike, maturity,
                                                                         div_periods, div_yield)
        edges_id = None
    else:
        # if submit endpoint was clicked
        submission_msg, excess_graph, envelope_graph, edges_id = utils.submit_endpoints(endpoints_btn, selected_nodes,
                                                                                        drift, vol, rate, init_price,
                                                                                        option, bermuda, option_type,
                                                                                        strike, maturity,
                                                                                        div_periods, div_yield)

    return submission_msg, excess_graph, envelope_graph, edges_id


if __name__ == '__main__':
    app.run_server(debug=True)
