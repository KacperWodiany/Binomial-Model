import src.options as op

payoff_dict = {
    'European': {
        'Call': op.european_call,
        'Put': op.european_put
    },
    'American': {
        'Call': op.american_call,
        'Put': op.american_put
    }
}