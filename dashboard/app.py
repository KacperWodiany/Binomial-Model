import dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px

from dash.dependencies import Input, Output, State

import layout
import params_labels
import default_params
from utils import generate_table_content

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
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
            html.B('Risk-Free Interest Rate'),
            html.Br(),
            dcc.Input(
                id='rate-input',
                **layout.rate_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Volatility'),
            html.Br(),
            dcc.Input(
                id='vol-input',
                **layout.vol_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Drift'),
            html.Br(),
            dcc.Input(
                id='drift-input',
                **layout.drift_input
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
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Initial Price'),
            html.Br(),
            dcc.Input(
                id='price-input',
                **layout.price_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='generate-button',
            **layout.generate_button
        ),

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
            ),
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
            ),
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='valuate-button',
            **layout.valuate_button
        ),

        html.P(),

        html.Div(
            id='current-option-container',
            style={'display': 'inline-block'}
        ),

        html.Div(
            id='current-stock-container',
            style={'display': 'inline-block'}
        )
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
    Input('trading-days-input', 'value')
)
def set_max_maturity(trading_days):
    return trading_days


@app.callback(
    Output('generate-button', 'disabled'),
    Output('generate-button', 'style'),
    Input('stock-dropdown', 'value'),
    Input('rate-input', 'value'),
    Input('vol-input', 'value'),
    Input('drift-input', 'value'),
    Input('trading-days-input', 'value'),
    Input('price-input', 'value')
)
def enable_generate_button(*stock_params):
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
    Output('valuate-button', 'disabled'),
    Output('valuate-button', 'style'),
    Input('generate-button', 'n_clicks'),
    Input('option-type-dropdown', 'value'),
    Input('strike-input', 'value'),
    Input('maturity-input', 'value'),
    Input('up-bar-input', 'value'),
    Input('low-bar-input', 'value')
)
def enable_valuate_button(gen_btn, *option_params):
    border_style = '2px solid '
    value_is_missing = any((param is None for param in option_params))
    if value_is_missing or gen_btn == 0:
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
    Input('valuate-button', 'n_clicks'),
    State('stock-dropdown', 'value'),
    State('rate-input', 'value'),
    State('vol-input', 'value'),
    State('drift-input', 'value'),
    State('trading-days-input', 'value'),
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
def handle_submitting_parameters(gen_btn, val_btn, *states):
    ctx = dash.callback_context
    nb_stock_params = len(params_labels.stock)
    stock_states = states[:nb_stock_params]
    option_states = states[nb_stock_params:]
    if ctx.triggered[0]['prop_id'] == 'generate-button.n_clicks':
        stock_content = generate_table_content(params_labels.stock, stock_states)
        option_content = None
    else:
        # when ctx.triggered[0]['prop_id'] == 'valuate-button.n_clicks':
        # need to be changed to elif when new Input added
        stock_content = generate_table_content(params_labels.stock, stock_states)
        option_content = generate_table_content(params_labels.option, option_states)

    stock_container = html.Table(stock_content)
    option_container = html.Table(option_content)

    return stock_container, option_container


if __name__ == '__main__':
    app.run_server(debug=True)
