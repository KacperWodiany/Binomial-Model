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

bermuda_seasons_dropdown = {
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
    'min': 0,
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
    'children': 'Generate',
    'style': {'border': '2px solid green','display': 'block', 'margin-left': '1vw'},
    'n_clicks': 0
}

tree_plot = {
    'layout': {'name': 'preset'},
    'style': {'width': '800px', 'height': '800px'}
}

select_path_button = {
    'children': 'Select Path',
    'n_clicks': 0,
    'style': {'display': 'none'}
}
