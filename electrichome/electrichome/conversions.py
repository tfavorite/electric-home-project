
FEET_TO_METERS = 0.3048
SQUARE_FEET_TO_METERS = 0.09290304
CELSIUS_FAHRENHEIT_MULTIPLIER = 1.8
FAHRENHEIT_FREEZE_POINT = 32

def feet_to_meters(value):
    return float(value) * FEET_TO_METERS


def squareft_to_squaremeter(value):
    return float(value) * SQUARE_FEET_TO_METERS


def celsius_to_fahrenheit(value):
    return float(value) * CELSIUS_FAHRENHEIT_MULTIPLIER + FAHRENHEIT_FREEZE_POINT


def fahrenheit_to_celsius(value):
    return (float(value) - FAHRENHEIT_FREEZE_POINT) / CELSIUS_FAHRENHEIT_MULTIPLIER
