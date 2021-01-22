import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
from dash.dependencies import Input, Output, State
from icecream import ic

import default_params
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
    else:
        stock_table = None
        option_table = None

    return stock_table, option_table


@app.callback(
    Output('tree-plot', 'elements'),
    Output('submit-path-button', 'style'),
    Output('submit-endpoints-button', 'style'),
    Input('generate-button', 'n_clicks'),
    Input('edges-id-container', 'children'),
    State('drift-input', 'value'),
    State('vol-input', 'value'),
    State('rate-input', 'value'),
    State('price-input', 'value'),
    State('maturity-input', 'value'),
    prevent_initial_call=True
)
def generate_tree_plot(gen_btn, edges_container, drift, vol, rate, init_price, maturity):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'generate-button.n_clicks':
        # if generate button was clicked only nodes are generated
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol)
        btn_style = {'border': '2px solid green'}
    elif edges_container is not None:
        # if endpoint was submitted nodes and respective edges are generated
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol)
        tree_elements.extend(utils.create_endpoint_path_markers(edges_container, maturity))
        btn_style = {'border': '2px solid green'}
    else:
        # All other cases. This one is not hurt layout since prevent_initial_call=True
        tree_elements = utils.generate_nodes(drift, init_price, maturity, rate, vol)
        btn_style = {'border': '2px solid green'}
    return tree_elements, btn_style, btn_style


@app.callback(
    Output('submission-msg', 'children'),
    Output('excess-plot-container', 'children'),
    Output('envelope-plot-container', 'children'),
    Output('edges-id-container', 'children'),
    Input('submit-path-button', 'n_clicks'),
    Input('submit-endpoints-button', 'n_clicks'),
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
    prevent_initial_call=True
)
def submit_prices(path_btn, endpoints_btn, selected_nodes, drift, vol, rate, init_price,
                  option, bermuda, option_type, strike, maturity):
    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'] == 'submit-path-button.n_clicks':
        submission_msg, excess_graph, envelope_graph = utils.submit_path(path_btn, selected_nodes,
                                                                         drift, vol, rate, init_price,
                                                                         option, bermuda, option_type, strike, maturity)
        edges_id = None
    else:
        # if submit endpoint was clicked
        submission_msg, excess_graph, envelope_graph, edges_id = utils.submit_endpoints(endpoints_btn, selected_nodes,
                                                                                        drift, vol, rate, init_price,
                                                                                        option, bermuda, option_type,
                                                                                        strike, maturity)

    return submission_msg, excess_graph, envelope_graph, edges_id


if __name__ == '__main__':
    app.run_server(debug=True)
