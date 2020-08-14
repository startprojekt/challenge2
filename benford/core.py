import csv
import io
import math
import re
from decimal import Decimal

from pydash import get

from benford.utils import calc_percentage, round_decimal


class BenfordAnalyzer:
    def __init__(self, occurences=None):
        self.percentages = None
        self.occurences = occurences or {}
        if self.occurences:
            self.calculate_percentages()

    @classmethod
    def create_from_string(cls, payload: str, relevant_column=0):
        return cls.create_from_csv(
            io.StringIO(payload), relevant_column=relevant_column)

    @classmethod
    def create_from_csv(cls, data, relevant_column=0):
        reader = csv.reader(data)
        occurences = {}
        for row in reader:
            significant_digit = get_first_significant_digit(row[relevant_column])
            if significant_digit not in occurences:
                occurences[significant_digit] = 1
            else:
                occurences[significant_digit] += 1
        return BenfordAnalyzer(occurences)

    @staticmethod
    def calculate_probability(digit, base=10):
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
        return round_decimal(math.log(1 + 1/digit, base), 3)

    def calculate_percentages(self) -> None:
        self.percentages = count_occurences_with_percentage(self.occurences)

    def get_percentage_of(self, digit: int) -> Decimal:
        return get(self.percentages, str(digit), Decimal('0'))


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


def count_occurences_with_percentage(occurences: dict, decimal_places: int = 1):
    result = {}
    percent_remaining = Decimal('100')
    total_occurences = sum(occurences.values())

    for k, v in occurences.items():
        v_percent = calc_percentage(v, total_occurences, decimal_places)
        if v_percent > percent_remaining:
            v_percent = percent_remaining
        result[k] = v_percent
        percent_remaining -= v_percent

    assert percent_remaining == 0, 'Sum of occurence percentages is not 100%.'
    return result
