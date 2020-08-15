import math
import re
from decimal import Decimal

from benford.conf import DEFAULT_BASE
from benford.exceptions import NoSignificantDigitFound
from benford.utils import calc_percentage, round_decimal

EXPECTED_BENFORD_LAW_DISTRIBUTION = {
    1: Decimal('30.1'),
    2: Decimal('17.6'),
    3: Decimal('12.5'),
    4: Decimal('9.7'),
    5: Decimal('7.9'),
    6: Decimal('6.7'),
    7: Decimal('5.8'),
    8: Decimal('5.1'),
    9: Decimal('4.6'),
}


def get_expected_distribution_flat(base=DEFAULT_BASE):
    return [get_expected_distribution(i + 1) for i in range(base - 1)]


def get_expected_distribution(digit, base=DEFAULT_BASE):
    """
    Calculates probability of occurence of `digit` as first digit in a number
    for a given base (decimal as default).

    Implementation based on:
    https://en.wikipedia.org/wiki/Benford%27s_law#Benford's_law_in_other_bases

    :param digit: First significant digit to be checked.
    :param base: Base to calculate for.
    :return:
    """
    assert base >= 2, 'Base must be greater or equal 2'
    return round_decimal(100 * math.log(1 + 1 / digit, base), 1)


re_first_sig_digit = re.compile(r'[1-9]')


def get_first_significant_digit(value) -> int:
    string = str(value)
    match = re_first_sig_digit.search(string)
    if match and match.group():
        return int(match[0])
    raise NoSignificantDigitFound(value)


def map_significant_digits(samples: iter):
    return map(lambda x: get_first_significant_digit(x), samples)


def count_occurences(samples: list, search_for_values=None) -> dict:
    """
    Counts occurences of values in samples.
    """
    result = {}
    values_to_count = search_for_values if search_for_values else set(samples)
    for v in values_to_count:
        result[v] = samples.count(v)
    return result


def count_occurences_with_percentage(occurences: dict, decimal_places: int = 1):
    result = {}
    percent_remaining = Decimal('100')
    total_occurences = sum(occurences.values())
    k = None

    for k, v in occurences.items():
        v_percent = calc_percentage(v, total_occurences, decimal_places)
        if v_percent > percent_remaining:
            v_percent = percent_remaining
        result[k] = v_percent
        percent_remaining -= v_percent
    if percent_remaining != 0:
        result[k] += percent_remaining
        percent_remaining = 0

    assert percent_remaining == 0, 'Sum of occurence percentages is not 100%.'
    return result


def get_degrees_of_freedom_for_base(base):
    return base - 1
