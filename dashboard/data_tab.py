import dash_core_components as dcc
import dash_html_components as html

import data_tab_layout

content = html.Div([
    html.Div([

        html.Div([
            html.B('Stock'),
            html.Br(),
            dcc.Dropdown(
                id='stock-dropdown',
                **data_tab_layout.stock_dropdown
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Risk-Free Interest Rate'),
            html.Br(),
            dcc.Input(
                id='rate-input',
                **data_tab_layout.rate_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Volatility'),
            html.Br(),
            dcc.Input(
                id='vol-input',
                **data_tab_layout.vol_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Drift'),
            html.Br(),
            dcc.Input(
                id='drift-input',
                **data_tab_layout.drift_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Number of Trading Days'),
            html.Br(),
            dcc.Input(
                id='trading-days-input',
                **data_tab_layout.trading_days_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Initial Price'),
            html.Br(),
            dcc.Input(
                id='price-input',
                **data_tab_layout.price_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='generate-button',
            **data_tab_layout.generate_button
        ),

        html.Div(id='current-stock-container')

    ], style={'display': 'inline-block', 'margin-left': '1vw'}),

    html.Div([

        html.Div([
            html.B('Option Type'),
            html.Br(),
            dcc.Dropdown(
                id='option-type-dropdown',
                **data_tab_layout.option_type_dropdown
            )
        ]),

        html.P(),

        html.Div([
            dcc.RadioItems(
                id='call-put-radio',
                **data_tab_layout.call_put_radio
            )
        ]),

        html.P(),

        html.Div([
            html.B('Strike'),
            html.Br(),
            dcc.Input(
                id='strike-input',
                **data_tab_layout.strike_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.B('Maturity'),
            html.Br(),
            dcc.Input(
                id='maturity-input',
                **data_tab_layout.maturity_input
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Upper Barrier'),
            html.Br(),
            dcc.Input(
                id='up-bar-input',
                **data_tab_layout.up_bar_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                id='up-bar-radio',
                **data_tab_layout.up_bar_radio
            ),
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Div([
            html.B('Lower Barrier'),
            html.Br(),
            dcc.Input(
                id='low-bar-input',
                **data_tab_layout.low_bar_input
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                id='low-bar-radio',
                **data_tab_layout.low_bar_radio
            )
        ], style={'display': 'inline-block'}),

        html.P(),

        html.Button(
            id='valuate-button',
            **data_tab_layout.valuate_button
        ),

        html.P(),

        html.Div(id='current-option-container')

    ], style={'display': 'inline-block', 'margin-right': '30vw', 'float': 'right'})
])
