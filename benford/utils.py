import decimal
import random
import string
from decimal import Decimal


def get_rounding_exponent(decimal_places: int = 0) -> str:
    return '1.' + '0' * decimal_places


def round_decimal(value, decimal_places=0, rounding=decimal.ROUND_HALF_UP) -> Decimal:
    if not isinstance(value, Decimal):
        value = Decimal(value)
    return value.quantize(
        Decimal(get_rounding_exponent(decimal_places)),
        rounding=rounding)


def calc_percentage(value, total, decimal_places: int = 1) -> Decimal:
    return round_decimal(100 * value / total, decimal_places)


def generate_random_identifier(length=10):
    letters_and_digits = string.ascii_lowercase
    return ''.join((random.choice(letters_and_digits) for i in range(length)))
