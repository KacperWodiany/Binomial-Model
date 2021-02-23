stock_dropdown = {
    'options': [
        {'label': 'Microsoft Corporation Common Stock', 'value': 'Microsoft'},
        {'label': 'Alphabet Inc. Class C Capital Stock', 'value': 'Google'},
        {'label': 'Custom Stock', 'value': 'custom'}
    ],
    'placeholder': 'Select stock',
    'style': {'width': '350px'},
    'value': 'Microsoft'
}

dividend_freq_dropdown = {
    'options': [{'label': 'No Dividend', 'value': 0}] + [{'label': 'every ' + str(x) + ' day(s)', 'value': x}
                                                         for x in (5, 10, 20, 40)],
    'style': {'width': '300px'},
    'value': 0
}

option_type_dropdown = {
    'options': [
        {'label': 'European', 'value': 'European'},
        {'label': 'American', 'value': 'American'},
        {'label': 'Bermuda', 'value': 'Bermuda'}
    ],
    'placeholder': 'Select option',
    'style': {'width': '350px'},
    'value': 'European'
}

bermuda_freq_dropdown = {
    'options': [{'label': 'every ' + str(x) + ' day(s)', 'value': x} for x in (5, 10, 20, 40)],
    'style': {'width': '300px'},
    'value': None
}

call_put_dropdown = {
    'options': [
        {'label': 'Call', 'value': 'Call'},
        {'label': 'Put', 'value': 'Put'}
    ],
    'style': {'width': '100px'},
    'value': 'Call',
}

drift_input = {
    'type': 'number',
    'min': -1,
    'max': 1
}

vol_input = {
    'type': 'number',
    'min': 0,
    'max': 1
}

rate_input = {
    'type': 'number',
    'min': 0,
    'max': 1,
    'value': 4e-5 * 252
}

dividend_yield_input = {
    'type': 'number',
    'min': 0,
    'max': 1,
    'value': 0
}

price_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

strike_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

maturity_input = {
    'type': 'number',
    'min': 1,
    'max': 252,
    'step': 1,
    'value': 10,
    'style': {'width': '100px'}
}

generate_button = {
    'children': 'Generate Prices',
    'style': {'border': '2px solid green', 'display': 'block', 'margin-left': '1vw'},
    'n_clicks': 0
}

heatmap_dropdown = {
    'options': [
        {'label': 'Stock Price', 'value': 'Stock_Price'},
        {'label': 'Payoff', 'value': 'Payoff'},
        {'label': 'Snells Envelope', 'value': 'Snell'},
        {'label': 'Stopping Time', 'value': 'If_Stopping_Time'},
        {'label': 'Cash in Trading Strategy', 'value': 'ksi_0'},
        {'label': 'Stock in Trading Strategy', 'value': 'ksi_1'},
        {'label': 'Excess Process Increment', 'value': 'Difference'}
    ],
    'style': {'width': '350px', 'display': 'none'},
    'value': 'Snell'
}

tree_plot = {
    'layout': {'name': 'preset'},
    'style': {'width': '800px', 'height': '800px'}
}

submit_path_button = {
    'children': 'Submit Path',
    'n_clicks': 0,
    'style': {'display': 'none'}
}

submit_endpoints_button = {
    'children': 'Submit Endpoint',
    'n_clicks': 0,
    'style': {'display': 'none'}
}
