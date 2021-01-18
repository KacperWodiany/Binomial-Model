from math import sqrt
vol = {
    'Microsoft': round(1.04e-2 * sqrt(252), 5),
    'Google': round(1.21e-2 * sqrt(252), 5),
    'custom': .05,
    None: 0
}

drift = {
    'Microsoft': round(6e-4 * 252, 5),
    'Google': round(9e-4 * 252, 5),
    'custom': 0,
    None: 0
}

price = {
    'Microsoft': 64.94,
    'Google': 835.24,
    'custom': 1,
    None: 1
}
