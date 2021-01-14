import dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px

from dash.dependencies import Input, Output, State

import app_params
import params_defaults

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.Div([

        html.Div([
            html.B('Stock'),
            html.Br(),
            dcc.Dropdown(
                id='stock-dropdown',
                **app_params.stock_dropdown
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Risk-Free Interest Rate'),
            html.Br(),
            dcc.Input(
                id='rate-input',
                **app_params.rate_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Volatility'),
            html.Br(),
            dcc.Input(
                id='vol-input',
                **app_params.vol_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Drift'),
            html.Br(),
            dcc.Input(
                id='drift-input',
                **app_params.drift_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Number of Periods'),
            html.Br(),
            dcc.Input(
                id='periods-input',
                **app_params.periods_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Initial Price'),
            html.Br(),
            dcc.Input(
                id='price-input',
                **app_params.price_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='generate-button',
            **app_params.generate_button
        ),

        html.P(),

        html.Div([
            html.B('Option'),
            html.Br(),
            dcc.Dropdown(
                id='option-dropdown',
                **app_params.option_dropdown
            )
        ]),

        html.P(),

        html.Div([
            html.B('Strike'),
            html.Br(),
            dcc.Input(
                id='strike-input',
                **app_params.strike_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Maturity'),
            html.Br(),
            dcc.Input(
                id='maturity-input',
                **app_params.maturity_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='valuate-button',
            **app_params.valuate_button
        ),

        html.P(),

        html.B('Currently submitted parameters'),
        html.Div([
            html.Div(id='currentStock'),
            html.Div(id='currentRate'),
            html.Div(id='currentVol'),
            html.Div(id='currentDrift'),
            html.Div(id='currentPeriods'),
            html.Div(id='currentPrice'),
            html.Br(),
            html.Div(id='currentOption'),
            html.Div(id='currentStrike'),
            html.Div(id='currentMaturity')
        ])
    ])
])


@app.callback(
    Output(component_id='vol-input', component_property='value'),
    Output(component_id='drift-input', component_property='value'),
    Output(component_id='strike-input', component_property='value'),
    Output(component_id='price-input', component_property='value'),
    Input(component_id='stock-dropdown', component_property='value')
)
def set_default_values(stock):
    return params_defaults.vol[stock], \
           params_defaults.drift[stock], \
           params_defaults.price[stock], \
           params_defaults.price[stock],


@app.callback(
    Output(component_id='maturity-input', component_property='value'),
    Input(component_id='periods-input', component_property='value')
)
def set_default_maturity(periods):
    return periods


@app.callback(
    Output(component_id='maturity-input', component_property='max'),
    Input(component_id='periods-input', component_property='value')
)
def set_maximum_maturity(periods):
    return periods


@app.callback(
    Output(component_id='generate-button', component_property='disabled'),
    Output(component_id='generate-button', component_property='style'),
    Input(component_id='stock-dropdown', component_property='value'),
    Input(component_id='rate-input', component_property='value'),
    Input(component_id='vol-input', component_property='value'),
    Input(component_id='drift-input', component_property='value'),
    Input(component_id='periods-input', component_property='value'),
    Input(component_id='price-input', component_property='value')
)
def disable_generate_button(stock, rate, vol, drift, periods, price):
    disabled_style = '2px solid '
    value_is_missing = any((x is None for x in (stock, rate, vol, drift, periods, price)))
    if value_is_missing:
        is_disabled = True
        disabled_style += 'red'
    else:
        is_disabled = False
        disabled_style += 'green'
    return is_disabled, {'border': disabled_style}


@app.callback(
    Output(component_id='valuate-button', component_property='disabled'),
    Output(component_id='valuate-button', component_property='style'),
    Input(component_id='option-dropdown', component_property='value'),
    Input(component_id='strike-input', component_property='value'),
    Input(component_id='maturity-input', component_property='value'),
    Input(component_id='generate-button', component_property='n_clicks')
)
def disable_valuate_button(option, strike, maturity, generate_n_clicks):
    disabled_style = '2px solid '
    value_is_missing = any((x is None for x in (option, strike, maturity)))
    if value_is_missing or generate_n_clicks == 0:
        is_disabled = True
        disabled_style += 'red'
    else:
        is_disabled = False
        disabled_style += 'green'
    return is_disabled, {'border': disabled_style}


@app.callback(
    Output(component_id='currentStock', component_property='children'),
    Output(component_id='currentRate', component_property='children'),
    Output(component_id='currentVol', component_property='children'),
    Output(component_id='currentDrift', component_property='children'),
    Output(component_id='currentPeriods', component_property='children'),
    Output(component_id='currentPrice', component_property='children'),
    Input(component_id='generate-button', component_property='n_clicks'),
    State(component_id='stock-dropdown', component_property='value'),
    State(component_id='rate-input', component_property='value'),
    State(component_id='vol-input', component_property='value'),
    State(component_id='drift-input', component_property='value'),
    State(component_id='periods-input', component_property='value'),
    State(component_id='price-input', component_property='value')
)
def display_current_stock_parameters(generate_n_clicks, stock, rate, vol, drift, periods, price):
    msft = 'Microsoft Corporation Common Stock'
    goog = 'Alphabet Inc. Class C Capital Stock'
    stock = msft if stock == 'msft' else goog
    values = (stock, rate, vol, drift, periods, price)
    prefixes = (
        'Stock: ',
        'Risk-Free Interest Rate: ',
        'Volatility: ',
        'Drift: ',
        'Number of Periods: ',
        'Initial Price: '
    )
    if generate_n_clicks > 0:
        current_params = tuple(prefix + str(value) for prefix, value in zip(prefixes, values))
    else:
        current_params = tuple('' for _ in range(len(values)))
    return current_params


@app.callback(
    Output(component_id='currentOption', component_property='children'),
    Output(component_id='currentStrike', component_property='children'),
    Output(component_id='currentMaturity', component_property='children'),
    Input(component_id='valuate-button', component_property='n_clicks'),
    State(component_id='option-dropdown', component_property='value'),
    State(component_id='strike-input', component_property='value'),
    State(component_id='maturity-input', component_property='value')
)
def display_current_option_parameters(valuate_n_clicks, option, strike, maturity):
    values = (option.replace('-', ' ').title(),
              strike,
              maturity)
    prefixes = (
        'Option: ',
        'Strike: ',
        'Maturity: '
    )
    if valuate_n_clicks > 0:
        current_params = tuple(prefix + str(value) for prefix, value in zip(prefixes, values))
    else:
        current_params = tuple('' for _ in range(len(values)))
    return current_params


if __name__ == '__main__':
    app.run_server(debug=True)
