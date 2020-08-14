import re
from decimal import Decimal

from benford.utils import calc_percentage


def get_first_significant_digit(value) -> int:
    string = str(value)
    match = re.search(r'[1-9]', string)
    if match and match.group():
        return int(match[0])
    raise ValueError('No significant digit found for `{0}`.'.format(value))


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


def count_occurences_with_percentage(samples: list, decimal_places: int = 1):
    occurences = count_occurences(samples)
    total_occurences = sum(occurences.values())
    result = {}
    percent_remaining = Decimal('100')

    for k, v in occurences.items():
        v_percent = calc_percentage(v, total_occurences, decimal_places)
        if v_percent > percent_remaining:
            v_percent = percent_remaining
        result[k] = (v, v_percent)
        percent_remaining -= v_percent

    assert percent_remaining == 0, 'Sum of occurence percentages is not 100%.'
    return result
