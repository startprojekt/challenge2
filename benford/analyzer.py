import csv
import io
from decimal import Decimal

import numpy
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.forms import Form
from pydash import get
from scipy.stats import chisquare

from benford.conf import DEFAULT_BASE
from benford.core import (
    get_first_significant_digit, get_expected_distribution, get_expected_distribution_flat,
    count_occurences_with_percentage, get_degrees_of_freedom_for_base,
)
from benford.exceptions import NoSignificantDigitFound
from benford.models import Dataset, SignificantDigit


class BenfordAnalyzer:
    def __init__(
            self, occurences=None,
            base=DEFAULT_BASE,
            error_rows: set = None,
            dataset: Dataset = None,
            title: str = ''
    ):
        self.dataset = dataset or Dataset(title=title)
        self.percentages = {}
        if dataset is not None:
            self._occurences = dataset.get_occurences_summary()
        else:
            self._occurences = occurences or {}
        self._error_rows = error_rows or set()
        self._total_occurences = sum(occurences.values()) if occurences else 0
        self._base = base
        if self._occurences:
            self.calculate_percentages()

    @classmethod
    def create_from_model(cls, dataset: Dataset):
        return BenfordAnalyzer(dataset=dataset)

    @classmethod
    def create_from_form(cls, form: Form):
        kwargs = {
            'relevant_column': get(form.cleaned_data, 'relevant_column', 0) or 0,
            'has_header': get(form.cleaned_data, 'has_header', False),
            'title': form.cleaned_data['title'],
        }
        data_file = form.cleaned_data['data_file']
        if data_file:
            return cls.create_from_file(data_file, **kwargs)
        else:
            return cls.create_from_string(form.cleaned_data['data_raw'], **kwargs)

    @classmethod
    def create_from_string(cls, payload: str, **kwargs):
        return cls.create_from_csv(
            io.StringIO(payload), **kwargs)

    @classmethod
    def create_from_file(cls, data_file: File, **kwargs):
        return cls.create_from_csv(
            io.StringIO(data_file.read().decode('utf-8')), **kwargs
        )

    @classmethod
    def create_from_csv(
            cls, data, delimiter='\t', **kwargs
    ):
        relevant_column = get(kwargs, 'relevant_column', 0) or 0
        has_header = get(kwargs, 'has_header', False)
        title = get(kwargs, 'title', '')
        occurences = {}
        reader = csv.reader(data, delimiter=delimiter)
        row_i = 0
        _error_rows = set()

        if has_header:
            # Skip first row (header).
            next(reader)

        for row in reader:
            _invalid_row = False
            try:
                significant_digit = get_first_significant_digit(row[relevant_column])
            except NoSignificantDigitFound:
                significant_digit = None
                _error_rows.add(row_i)
            finally:
                row_i += 1

            if significant_digit is None:
                continue

            if significant_digit not in occurences:
                occurences[significant_digit] = 1
            else:
                occurences[significant_digit] += 1

        return BenfordAnalyzer(occurences, error_rows=_error_rows, title=title)

    @staticmethod
    def get_expected_distribution(digit, base=DEFAULT_BASE):
        return get_expected_distribution(digit, base)

    @staticmethod
    def get_expected_distribution_flat(base=DEFAULT_BASE):
        return get_expected_distribution_flat(base)

    @property
    def base(self):
        return self._base

    @property
    def title(self):
        return self.dataset.title

    @property
    def occurences(self):
        return self._occurences

    @property
    def total_occurences(self):
        return self._total_occurences

    @property
    def has_errors(self):
        return bool(self._error_rows)

    @property
    def error_rows(self):
        return self._error_rows

    def calculate_percentages(self) -> None:
        self.percentages = count_occurences_with_percentage(self.occurences)

    def get_observed_distribution(self, digit: int) -> Decimal:
        return get(self.percentages, str(digit), Decimal('0'))

    def get_observed_distribution_flat(self, base=DEFAULT_BASE):
        result = numpy.zeros(base - 1)
        for digit, percent in self.percentages.items():
            result[digit - 1] = percent
        return result

    def check_compliance_with_benford_law(self, base=DEFAULT_BASE):
        c = chisquare(
            f_obs=list(map(lambda x: float(x), self.get_observed_distribution_flat(base))),
            f_exp=list(map(lambda x: float(x), self.get_expected_distribution_flat(base))),
            ddof=get_degrees_of_freedom_for_base(base),
        )
        return c

    def get_digits_list(self):
        return range(1, self.base)

    def save(self):
        self.dataset.save()
        new_digits = []
        existing_digits = []

        for digit, occurences in self.occurences.items():
            try:
                significant_digit = self.dataset.significant_digits.get(digit=digit)
                significant_digit.occurences = occurences
                existing_digits.append(significant_digit)
            except ObjectDoesNotExist:
                significant_digit = SignificantDigit(
                    dataset=self.dataset,
                    digit=digit,
                    occurences=occurences,
                )
                new_digits.append(significant_digit)

        if new_digits:
            SignificantDigit.objects.bulk_create(new_digits)

        if existing_digits:
            SignificantDigit.objects.bulk_create(existing_digits, ['occurences', ])

        return self.dataset
