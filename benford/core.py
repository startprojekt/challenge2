import csv
import io
import math
import re
from decimal import Decimal

from django.forms import Form
from pydash import get

from benford.exceptions import NoSignificantDigitFound
from benford.utils import calc_percentage, round_decimal


class BenfordAnalyzer:
    def __init__(self, occurences=None, base=10, error_rows=0):
        self.percentages = {}
        self._occurences = occurences or {}
        self._error_rows = error_rows
        self._total_occurences = sum(occurences.values()) if occurences else 0
        self._base = base
        if self._occurences:
            self.calculate_percentages()

    @classmethod
    def create_from_form(cls, form: Form):
        return cls.create_from_string(
            form.cleaned_data['data_raw'],
            relevant_column=get(form.cleaned_data, 'relevant_column', 0) or 0,
            has_header=get(form.cleaned_data, 'has_header', False),
        )

    @classmethod
    def create_from_string(cls, payload: str, relevant_column=0, has_header: bool = False):
        return cls.create_from_csv(
            io.StringIO(payload),
            relevant_column=relevant_column,
            has_header=has_header)

    @classmethod
    def create_from_csv(
            cls, data, delimiter='\t',
            relevant_column: int = 0,
            has_header: bool = False,
    ):
        occurences = {}
        reader = csv.reader(data, delimiter=delimiter)
        row_i = 0
        _error_rows = 0

        if has_header:
            # Skip first row (header).
            next(reader)

        for row in reader:
            _invalid_row = False
            try:
                significant_digit = get_first_significant_digit(row[relevant_column])
            except NoSignificantDigitFound:
                significant_digit = None
                _error_rows += 1
            finally:
                row_i += 1

            if significant_digit is None:
                continue

            if significant_digit not in occurences:
                occurences[significant_digit] = 1
            else:
                occurences[significant_digit] += 1

        return BenfordAnalyzer(occurences, error_rows=_error_rows)

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
        return round_decimal(math.log(1 + 1 / digit, base), 3)

    @property
    def base(self):
        return self._base

    @property
    def occurences(self):
        return self._occurences

    @property
    def total_occurences(self):
        return self._total_occurences

    @property
    def has_errors(self):
        return self._error_rows > 0

    def calculate_percentages(self) -> None:
        self.percentages = count_occurences_with_percentage(self.occurences)

    def get_percentage_of(self, digit: int) -> Decimal:
        return get(self.percentages, str(digit), Decimal('0'))


def get_first_significant_digit(value) -> int:
    string = str(value)
    match = re.search(r'[1-9]', string)
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

    for k, v in occurences.items():
        v_percent = calc_percentage(v, total_occurences, decimal_places)
        if v_percent > percent_remaining:
            v_percent = percent_remaining
        result[k] = v_percent
        percent_remaining -= v_percent

    assert percent_remaining == 0, 'Sum of occurence percentages is not 100%.'
    return result
