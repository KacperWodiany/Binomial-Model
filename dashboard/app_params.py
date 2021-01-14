stock_dropdown = {
    'options': [
                    {'label': 'Microsoft Corporation Common Stock', 'value': 'msft'},
                    {'label': 'Alphabet Inc. Class C Capital Stock', 'value': 'goog'}
                ],
    'placeholder': 'Select stock',
    'style': {'width': '350px'},
    'value': 'msft'
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

periods_input = {
    'type': 'number',
    'min': 1,
    'max': 252,
    'step': 1,
    'value': 126,
    'style': {'width': '150px'}
}

price_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

generate_button = {
    'children': 'Generate Prices',
    'n_clicks': 0
}

option_dropdown = {
    'options': [
                    {'label': 'European Call', 'value': 'european-call'},
                    {'label': 'European Put', 'value': 'european-put'},
                    {'label': 'American Call', 'value': 'american-call'},
                    {'label': 'American Put', 'value': 'american-put'}
                ],
    'placeholder': 'Select option',
    'style': {'width': '350px'},
    'value': 'european-call'
}

strike_input = {
    'type': 'number',
    'min': 0,
    'max': 3000
}

maturity_input = {
    'type': 'number',
    'min': 1,
}

valuate_button = {
    'children': 'Valuate Option',
    'disabled': True,
    'n_clicks': 0,
    'style': {'border': '2px solid red'}
}
