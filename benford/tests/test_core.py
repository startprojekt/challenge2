from decimal import Decimal

from django.test.testcases import TestCase

from benford.core import (
    get_first_significant_digit, map_significant_digits, count_occurences,
    count_occurences_with_percentage,
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
        occurences_with_percentage_1 = count_occurences_with_percentage(significant_digits)
        self.assertDictEqual(
            occurences_with_percentage_1, {
                1: (7, Decimal('46.7')), 2: (2, Decimal('13.3')), 3: (3, Decimal('20')),
                # In some cases we can have same occurence values but
                # different percentages (sum of the percentages must be 100 and
                # it's forced on last value).
                4: (1, Decimal('6.7')), 5: (1, Decimal('6.7')), 6: (1, Decimal('6.6')),
            })

        # We can pass decimal_places to control percentage display/precision.
        occurences_with_percentage_2 = count_occurences_with_percentage(significant_digits, decimal_places=0)
        self.assertDictEqual(
            occurences_with_percentage_2, {
                1: (7, Decimal('47')), 2: (2, Decimal('13')), 3: (3, Decimal('20')),
                4: (1, Decimal('7')), 5: (1, Decimal('7')), 6: (1, Decimal('6')),
            })

        # Ensure we always have 100 percent for digit occurences.
        self.assertEqual(
            sum(map(lambda x: x[1], occurences_with_percentage_2.values())), 100)
