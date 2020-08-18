import csv
import io
from decimal import Decimal

import numpy
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import transaction
from django.forms import Form
from pydash import get
from scipy.stats import chisquare

from benford.conf import (
    DEFAULT_BASE, BENFORD_LAW_COMPLIANCE_STAT_SIG, DEFAULT_RELEVANT_COLUMN, DEFAULT_DELIMITER,
    ALLOWED_DELIMITERS,
)
from benford.core import (
    get_first_significant_digit, get_expected_distribution, get_expected_distribution_flat,
    count_occurences_with_percentage, get_degrees_of_freedom_for_base,
)
from benford.exceptions import NoSignificantDigitFound
from benford.models import Dataset, SignificantDigit, DatasetRow


class BenfordAnalyzer:
    def __init__(
            self, occurences=None,
            base=DEFAULT_BASE,
            error_rows: set = None,
            dataset: Dataset = None,
            title: str = '',
            input_data=None,
            delimiter=DEFAULT_DELIMITER,
    ):
        self.dataset = dataset or Dataset(title=title)
        self.percentages = {}
        self.input_data = input_data
        self.delimiter = delimiter

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
        return cls.create_from_csv(io.StringIO(payload), **kwargs)

    @classmethod
    def create_from_file(cls, data_file: File, **kwargs):
        return cls.create_from_csv(
            io.StringIO(data_file.read().decode('utf-8')), **kwargs)

    @classmethod
    def create_from_csv(
            cls,
            input_data: io.StringIO,
            delimiter='\t',
            relevant_column: int = None,
            has_header: bool = False,
            title: str = '',
    ):
        assert delimiter in ALLOWED_DELIMITERS, \
            f"The `delimiter` argument must be one of {ALLOWED_DELIMITERS}. " \
            f"Got `{delimiter}` instead."

        first_line: str = input_data.readline()
        delimiter = delimiter or auto_detect_delimiter(first_line) or DEFAULT_DELIMITER
        relevant_column = relevant_column or find_relevant_column(first_line)

        occurences = {}
        input_data.seek(0)
        reader = csv.reader(input_data, delimiter=delimiter)
        row_i = 0
        _error_rows = set()

        if has_header:
            # Skip first row (header).
            next(reader)

        for row in reader:
            _invalid_row = False
            try:
                significant_digit = get_first_significant_digit(row[relevant_column])
            except (NoSignificantDigitFound, IndexError):
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

        return BenfordAnalyzer(
            occurences,
            error_rows=_error_rows, title=title,
            input_data=input_data, delimiter=delimiter)

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

    @property
    def error_count(self):
        return len(self._error_rows)

    def calculate_percentages(self) -> None:
        self.percentages = count_occurences_with_percentage(self.occurences)

    def get_observed_distribution(self, digit: int) -> Decimal:
        return get(self.percentages, str(digit), Decimal('0'))

    def get_observed_distribution_flat(self, base=DEFAULT_BASE):
        result = numpy.zeros(base - 1)
        for digit, percent in self.percentages.items():
            result[digit - 1] = percent
        return result

    def get_chisq_test_statistic(self, base=DEFAULT_BASE):
        c = chisquare(
            f_obs=list(map(lambda x: float(x), self.get_observed_distribution_flat(base))),
            f_exp=list(map(lambda x: float(x), self.get_expected_distribution_flat(base))),
            ddof=get_degrees_of_freedom_for_base(base),
        )
        return c[0]

    @property
    def is_compliant_with_benford_law(self) -> bool:
        return self.get_chisq_test_statistic() <= BENFORD_LAW_COMPLIANCE_STAT_SIG

    def get_digits_list(self):
        return range(1, self.base)

    def save(self) -> Dataset:
        with transaction.atomic():
            dataset = self._perform_save()
            self._save_data_rows()
        return dataset

    def _perform_save(self) -> Dataset:
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
                    occurences=occurences)
                new_digits.append(significant_digit)

        if new_digits:
            SignificantDigit.objects.bulk_create(new_digits)

        if existing_digits:
            SignificantDigit.objects.bulk_create(existing_digits, ['occurences', ])

        return self.dataset

    def _save_data_rows(self):
        """
        Save user data input to browse later.
        """
        if self.input_data is None:
            return
        self.input_data.seek(0)
        line = 0
        rows = []
        reader = csv.reader(self.input_data, delimiter=self.delimiter)

        while True:
            try:
                row = next(reader)
            except StopIteration:
                break
            rows.append(DatasetRow(
                dataset=self.dataset,
                line=line, data=row,
                has_error=line in self.error_rows))
            line += 1

        # Bulk save rows.
        DatasetRow.objects.bulk_create(rows)

    def get_occurences_for_digit(self, digit) -> int:
        return get(self.occurences, digit, 0) or 0

    def get_percentage_for_digit(self, digit) -> int:
        return get(self.percentages, digit, 0) or 0

    def get_summary(self):
        summary = []
        for d in self.get_digits_list():
            row = AnalyzerSummaryRow(
                digit=d,
                occurences=self.get_occurences_for_digit(d),
                percentage=self.get_percentage_for_digit(d),
                expected_percentage=self.get_expected_distribution(d),
            )
            summary.append(row)
        return summary


class AnalyzerSummaryRow:
    def __init__(self, digit, occurences, percentage, expected_percentage):
        self.digit = digit
        self.occurences = occurences
        self.percentage = percentage
        self.expected_percentage = expected_percentage


def auto_detect_delimiter(row) -> str:
    for d in ALLOWED_DELIMITERS:
        if d in row:
            return d
    return DEFAULT_DELIMITER


def find_relevant_column(first_line: str, second_line: str = '', delimiter: str = None) -> int:
    """
    Finds a first column that contains a number. If it doesn't find it in
    the first line, it assumes it must be a header and analyzes the second line.

    :param first_line:
    :param second_line:
    :param delimiter:
    :return:
    """
    return (
            _find_relevant_column_on_line(first_line)
            or _find_relevant_column_on_line(second_line)
            or DEFAULT_RELEVANT_COLUMN)


def _find_relevant_column_on_line(line: str, delimiter: str = None) -> int:
    delimiter = delimiter or auto_detect_delimiter(line) or DEFAULT_DELIMITER
    reader = csv.reader(io.StringIO(line), delimiter=delimiter)

    try:
        row = next(reader)
    except StopIteration:
        return DEFAULT_RELEVANT_COLUMN

    column_no = 0
    first_number = None

    for v in row:
        try:
            first_number = float(v)
            break
        except ValueError:
            pass
        column_no += 1

    return column_no if first_number is not None else None
