
FEET_TO_METERS = 0.3048
SQUARE_FEET_TO_METERS = 0.09290304
CELSIUS_TO_FAHRENHEIT = 9 / 5 + 32
FAHRENHEIT_TO_CELSIUS = 5/9


def feet_to_meters(value):
    return float(value) * FEET_TO_METERS


def squareft_to_squaremeter(value):
    return float(value) * SQUARE_FEET_TO_METERS


def celsius_to_fahrenheit(value):
    return float(value) * CELSIUS_TO_FAHRENHEIT


def fahrenheit_to_celsius(value):
    return float(value) * FAHRENHEIT_TO_CELSIUS + 32
