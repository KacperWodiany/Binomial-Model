
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

price_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

rate_input = {
    'type': 'number',
    'min': 0,
    'max': 1,
    'value': 0.009
}

vol_input = {
    'type': 'number',
    'min': 0,
    'max': 1
}

drift_input = {
    'type': 'number',
    'min': 0,
    'max': 1
}

trading_days_input = {
    'type': 'number',
    'min': 1,
    'max': 252,
    'step': 1,
    'value': 126,
    'style': {'width': '250px'}
}

generate_button = {
    'children': 'Generate Prices',
    'n_clicks': 0
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

call_put_radio = {
    'options':  [
                    {'label': 'Call', 'value': 'Call'},
                    {'label': 'Put', 'value': 'Put'}
    ],
    'value': 'Call',
    'labelStyle': {'display': 'inline-block'}
}

strike_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

maturity_input = {
    'type': 'number',
    'min': 1
}

up_bar_input = {
    'type': 'number',
    'min': 0,
}

up_bar_radio = {
    'options':  [
                    {'label': 'Out', 'value': 'Out'},
                    {'label': 'In', 'value': 'In'}
    ],
    'labelStyle': {'display': 'inline-block'}
}

low_bar_input = {
    'type': 'number',
    'min': 0,
}

low_bar_radio = {
    'options':  [
                    {'label': 'Out', 'value': 'Out'},
                    {'label': 'In', 'value': 'In'}
    ],
    'labelStyle': {'display': 'inline-block'}
}

valuate_button = {
    'children': 'Valuate Option',
    'disabled': True,
    'n_clicks': 0,
    'style': {'border': '2px solid red'}
}

tree_plot = {
    'layout': {'name': 'preset'},
    'style': {'width': '100%', 'height': '400px'},
}
