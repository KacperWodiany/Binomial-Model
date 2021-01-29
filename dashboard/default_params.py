from math import sqrt
vol = {
    'Microsoft': round(1.21e-2 * sqrt(252), 5),
    'Google': round(1.04e-2 * sqrt(252), 5),
    'custom': None,
    None: None
}

drift = {
    'Microsoft': round(1.1e-3 * 252, 5),
    'Google': round(9e-4 * 252, 5),
    'custom': None,
    None: None
}

price = {
    'Microsoft': 64.94,
    'Google': 835.24,
    'custom': None,
    None: None
}
