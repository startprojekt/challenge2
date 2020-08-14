from decimal import Decimal

from django.test.testcases import TestCase

from benford.core import (
    get_first_significant_digit, map_significant_digits, count_occurences,
    count_occurences_with_percentage, BenfordAnalyzer,
)
from benford.tests.common import RAW_DATA_SAMPLE_1, INT_LIST_SAMPLE_1


class CoreTest(TestCase):
    def test_get_first_significant_digit(self):
        self.assertEqual(get_first_significant_digit(1), 1)
        self.assertEqual(get_first_significant_digit(2), 2)
        self.assertEqual(get_first_significant_digit(3), 3)
        self.assertEqual(get_first_significant_digit(4), 4)
        self.assertEqual(get_first_significant_digit(5), 5)
        self.assertEqual(get_first_significant_digit(6), 6)
        self.assertEqual(get_first_significant_digit(7), 7)
        self.assertEqual(get_first_significant_digit(8), 8)
        self.assertEqual(get_first_significant_digit(9), 9)
        self.assertEqual(get_first_significant_digit(10), 1)
        self.assertEqual(get_first_significant_digit(20), 2)
        self.assertEqual(get_first_significant_digit(0.1), 1)
        self.assertEqual(get_first_significant_digit(0.4), 4)
        self.assertEqual(get_first_significant_digit(0.9), 9)

        # Some invalid inputs
        with self.assertRaises(ValueError):
            get_first_significant_digit("ABC")

    def test_validate_input_data(self):
        sample = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 25, 33, 34, ]

        # Convert to list of significant digits.
        significant_digits = list(map_significant_digits(sample))
        self.assertListEqual(
            significant_digits,
            [1, 2, 3, 4, 5, 6, 1, 1, 1, 1, 1, 1, 2, 3, 3, ])

        # Count occurences.
        self.assertDictEqual(
            count_occurences(significant_digits),
            {1: 7, 2: 2, 3: 3, 4: 1, 5: 1, 6: 1})

        # We can force counting values that don't occur even once if we pass
        # second argument to `count_occurences`.
        self.assertDictEqual(
            count_occurences(significant_digits, set(range(1, 10))),
            {1: 7, 2: 2, 3: 3, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 0})

        # Count occurences and calculate their percentage.
        occurences_with_percentage_1 = count_occurences_with_percentage(
            count_occurences(significant_digits))
        self.assertDictEqual(
            occurences_with_percentage_1, {
                1: Decimal('46.7'), 2: Decimal('13.3'), 3: Decimal('20'),
                # In some cases we can have same occurence values but
                # different percentages (sum of the percentages must be 100 and
                # it's forced on last value).
                4: Decimal('6.7'), 5: Decimal('6.7'), 6: Decimal('6.6'),
            })

        # We can pass decimal_places to control percentage display/precision.
        occurences_with_percentage_2 = count_occurences_with_percentage(
            count_occurences(significant_digits), decimal_places=0)
        self.assertDictEqual(
            occurences_with_percentage_2, {
                1: Decimal('47'), 2: Decimal('13'), 3: Decimal('20'),
                4: Decimal('7'), 5: Decimal('7'), 6: Decimal('6'),
            })

        # Ensure we always have 100 percent for digit occurences.
        self.assertEqual(
            sum(occurences_with_percentage_2.values()), 100)


class BenfordAnalyzerTest(TestCase):
    def test_benford_analyzer(self):
        analyzer = BenfordAnalyzer(occurences={1: 10, 2: 3, 3: 5, 4: 8})
        self.assertEqual(len(analyzer.occurences), len(analyzer.percentages))

        # Retrieve percentages individually
        self.assertEqual(analyzer.get_percentage_of(1), Decimal('38.5'))
        self.assertEqual(analyzer.get_percentage_of(2), Decimal('11.5'))
        self.assertEqual(analyzer.get_percentage_of(3), Decimal('19.2'))
        self.assertEqual(analyzer.get_percentage_of(4), Decimal('30.8'))

        # Handle non-existent (not occured) digits.
        self.assertEqual(analyzer.get_percentage_of(9), Decimal('0'))

    def test_benford_law(self):
        analyzer = BenfordAnalyzer()

        # We assume base=10 as default.
        self.assertEqual(analyzer.calculate_probability(1), Decimal('0.301'))
        self.assertEqual(analyzer.calculate_probability(2), Decimal('0.176'))
        self.assertEqual(analyzer.calculate_probability(3), Decimal('0.125'))
        self.assertEqual(analyzer.calculate_probability(4), Decimal('0.097'))
        self.assertEqual(analyzer.calculate_probability(5), Decimal('0.079'))
        self.assertEqual(analyzer.calculate_probability(6), Decimal('0.067'))
        self.assertEqual(analyzer.calculate_probability(7), Decimal('0.058'))
        self.assertEqual(analyzer.calculate_probability(8), Decimal('0.051'))
        self.assertEqual(analyzer.calculate_probability(9), Decimal('0.046'))

        # Some calculations with other-than-10 bases.
        self.assertEqual(analyzer.calculate_probability(1, base=2), Decimal('1'))
        self.assertEqual(analyzer.calculate_probability(1, base=3), Decimal('0.631'))
        self.assertEqual(analyzer.calculate_probability(2, base=3), Decimal('0.369'))
