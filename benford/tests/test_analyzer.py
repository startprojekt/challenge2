from decimal import Decimal

from django.test.testcases import TestCase

from benford.analyzer import BenfordAnalyzer
from benford.core import (
    EXPECTED_BENFORD_LAW_DISTRIBUTION,
)
from benford.models import Dataset, SignificantDigit


class BenfordAnalyzerTest(TestCase):
    def test_benford_analyzer(self):
        analyzer = BenfordAnalyzer(occurences={1: 10, 2: 3, 3: 5, 4: 8})
        self.assertEqual(analyzer.base, 10)
        self.assertEqual(len(analyzer.occurences), len(analyzer.percentages))

        # Retrieve percentages individually
        self.assertEqual(analyzer.get_observed_distribution(1), Decimal('38.5'))
        self.assertEqual(analyzer.get_observed_distribution(2), Decimal('11.5'))
        self.assertEqual(analyzer.get_observed_distribution(3), Decimal('19.2'))
        self.assertEqual(analyzer.get_observed_distribution(4), Decimal('30.8'))

        # Handle non-existent (not occured) digits.
        self.assertEqual(analyzer.get_observed_distribution(9), Decimal('0'))

    def test_benford_law(self):
        analyzer = BenfordAnalyzer()

        # We assume base=10 as default.
        self.assertEqual(analyzer.get_expected_distribution(1), Decimal('30.1'))
        self.assertEqual(analyzer.get_expected_distribution(2), Decimal('17.6'))
        self.assertEqual(analyzer.get_expected_distribution(3), Decimal('12.5'))
        self.assertEqual(analyzer.get_expected_distribution(4), Decimal('9.7'))
        self.assertEqual(analyzer.get_expected_distribution(5), Decimal('7.9'))
        self.assertEqual(analyzer.get_expected_distribution(6), Decimal('6.7'))
        self.assertEqual(analyzer.get_expected_distribution(7), Decimal('5.8'))
        self.assertEqual(analyzer.get_expected_distribution(8), Decimal('5.1'))
        self.assertEqual(analyzer.get_expected_distribution(9), Decimal('4.6'))

        # Some calculations with other-than-10 bases.
        self.assertEqual(analyzer.get_expected_distribution(1, base=2), Decimal('100'))
        self.assertEqual(analyzer.get_expected_distribution(1, base=3), Decimal('63.1'))
        self.assertEqual(analyzer.get_expected_distribution(2, base=3), Decimal('36.9'))

    def test_save_models(self):
        self.assertEqual(Dataset.objects.count(), 0)
        self.assertEqual(SignificantDigit.objects.count(), 0)

        # We build some BenfordAnalyzer instance.
        analyzer = BenfordAnalyzer(occurences={
            1: 5735, 2: 3544, 3: 2341, 4: 1847, 5: 1559,
            6: 1370, 7: 1166, 8: 1042, 9: 903,
        })

        # And save it to database.
        analyzer.save()

        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(SignificantDigit.objects.count(), 9)

        dataset = Dataset.objects.first()

        digit_1: SignificantDigit = dataset.significant_digits.get(digit=1)
        self.assertEqual(digit_1.occurences, 5735)

        digit_2: SignificantDigit = dataset.significant_digits.get(digit=2)
        self.assertEqual(digit_2.occurences, 3544)

        digit_3: SignificantDigit = dataset.significant_digits.get(digit=3)
        self.assertEqual(digit_3.occurences, 2341)

    def test_benford_law_compliance(self):
        # We perform a test with an ideal set of data
        # that is 100% compliant with Benford's Law.
        analyzer = BenfordAnalyzer(occurences={
            1: 301, 2: 176, 3: 125,
            4: 97, 5: 79, 6: 67,
            7: 58, 8: 51, 9: 46,
        })

        self.assertListEqual(
            list(analyzer.get_observed_distribution_flat()),
            [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6],
        )

        self.assertListEqual(
            list(analyzer.get_expected_distribution_flat()),
            list(EXPECTED_BENFORD_LAW_DISTRIBUTION.values()),
        )

        self.assertEqual(analyzer.get_observed_distribution(1), Decimal('30.1'))
        self.assertEqual(analyzer.get_expected_distribution(1), Decimal('30.1'))

        chisq = analyzer.get_chisq_test_statistic()

        # An ideal case when all values match the expected distribution
        # according to Benford's law.
        self.assertEqual(chisq, 0)
        self.assertTrue(analyzer.is_compliant_with_benford_law)

    def test_benford_law_compliance_divergence(self):
        analyzer = BenfordAnalyzer(occurences={
            1: 100, 2: 80, 3: 60,
            4: 50, 5: 35, 6: 20,
            7: 18, 8: 13, 9: 10,
        })

        chisq = analyzer.get_chisq_test_statistic()
        self.assertEqual(chisq, 5.226832036302567)
        self.assertTrue(analyzer.is_compliant_with_benford_law)

    def test_benford_law_compliance_divergence_2(self):
        analyzer = BenfordAnalyzer(occurences={
            1: 1, 2: 2, 3: 3,
            4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9,
        })

        chisq = analyzer.get_chisq_test_statistic()
        self.assertEqual(chisq, 146.05630441745905)
        self.assertFalse(analyzer.is_compliant_with_benford_law)

    def test_digits_summary(self):
        analyzer = BenfordAnalyzer(occurences={1: 10, 2: 5, 3: 5})
        summary = analyzer.get_summary()
        self.assertEqual(len(summary), 9)
        self.assertEqual(summary[0].digit, 1)
        self.assertEqual(summary[0].occurences, 10)
        self.assertEqual(summary[0].percentage, Decimal('50'))
        self.assertEqual(summary[0].expected_percentage, Decimal('30.1'))

    def test_load_from_model(self):
        dataset = Dataset.objects.create(title='My dataset')
        SignificantDigit.objects.bulk_create([
            SignificantDigit(
                dataset=dataset, digit=1, occurences=30),
            SignificantDigit(
                dataset=dataset, digit=2, occurences=20),
            SignificantDigit(
                dataset=dataset, digit=3, occurences=10),
        ])

        analyzer = BenfordAnalyzer.create_from_model(dataset)
        self.assertEqual(analyzer.dataset.pk, dataset.pk)
        self.assertEqual(analyzer.title, 'My dataset')
