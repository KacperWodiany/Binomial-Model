import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import data_tab
import default_params
import params_labels
import plot_tab
import utils

# import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children=[
    dcc.Tabs(id='main-tabs',
             value='data-tab',
             children=[
                 dcc.Tab(label='Data', value='data-tab'),
                 dcc.Tab(label='Plots', value='plot-tab')
             ]),
    html.Div(id='main-tab-content')
])


@app.callback(Output('main-tab-content', 'children'),
              Input('main-tabs', 'value'))
def render_content(tab):
    if tab == 'data-tab':
        return data_tab.content
    elif tab == 'plot-tab':
        return plot_tab.content


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
    # We allow barriers to be not specified
    value_is_missing = any((param is None for param in option_params[:-2]))
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
        stock_content = utils.generate_table_content(params_labels.stock, stock_states)
        option_content = None
    else:
        # when ctx.triggered[0]['prop_id'] == 'valuate-button.n_clicks':
        # need to be changed to elif when new Input added
        stock_content = utils.generate_table_content(params_labels.stock, stock_states)
        option_content = utils.generate_table_content(params_labels.option, option_states)

    stock_container = html.Table(stock_content)
    option_container = html.Table(option_content)

    return stock_container, option_container


if __name__ == '__main__':
    app.run_server(debug=True)
