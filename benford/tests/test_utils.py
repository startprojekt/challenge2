from decimal import Decimal

from django.test.testcases import TestCase

from benford.utils import calc_percentage, round_decimal


class RoundDecimalTest(TestCase):
    def test_rounding_decimals(self):
        self.assertEqual(
            round_decimal(Decimal('1.234')),
            Decimal('1'))

        self.assertEqual(
            round_decimal(Decimal('34.321'), decimal_places=0),
            Decimal('34'))

        self.assertEqual(
            round_decimal(Decimal('34.367'), decimal_places=1),
            Decimal('34.4'))


class CalcPercentageTest(TestCase):
    def test_calc_percentage(self):
        # Simple calculations
        self.assertEqual(calc_percentage(1, 1), Decimal('100'))
        self.assertEqual(calc_percentage(1, 10), Decimal('10'))
        self.assertEqual(calc_percentage(5, 10), Decimal('50'))
        self.assertEqual(calc_percentage(10, 1), Decimal('1000'))

        # Let's add some fractions
        self.assertEqual(calc_percentage(3442, 10000), Decimal('34.4'))
        self.assertEqual(calc_percentage(3447, 10000), Decimal('34.5'))
