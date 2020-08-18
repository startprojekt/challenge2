from decimal import Decimal

from django.test import SimpleTestCase
from django.test.testcases import TestCase

from benford.analyzer import (
    BenfordAnalyzer, auto_detect_delimiter, find_relevant_column, DEFAULT_DELIMITER,
    DEFAULT_RELEVANT_COLUMN,
)
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


class AnalyzerHelperFunctionsTest(SimpleTestCase):
    def test_auto_detect_delimiter(self):
        self.assertEqual(auto_detect_delimiter("1"), DEFAULT_DELIMITER)
        self.assertEqual(auto_detect_delimiter("a\t1"), "\t")
        self.assertEqual(auto_detect_delimiter("a;b;1"), ";")
        self.assertEqual(auto_detect_delimiter("a,b,c,1"), ",")
        self.assertEqual(auto_detect_delimiter("a,b;c;1"), ";")

    def test_auto_find_relevant_column(self):
        self.assertEqual(find_relevant_column("1"), 0)
        self.assertEqual(find_relevant_column("a;b;1"), 2)
        self.assertEqual(find_relevant_column("a\t1"), 1)
        self.assertEqual(find_relevant_column("a\tb\tc\t1"), 3)

        # If we don't find a relevant column
        # we leave it by a default value (DEFAULT_RELEVANT_COLUMN)
        self.assertEqual(
            find_relevant_column("a\tb\tc\td"), DEFAULT_RELEVANT_COLUMN)
        self.assertEqual(
            find_relevant_column("a\tb2\tc3\td"), DEFAULT_RELEVANT_COLUMN)

        # If we provide two lines (the first one can be a header) it also
        # will be analyzed.
        self.assertEqual(find_relevant_column(
            first_line="a\tb\tc\td",
            second_line="x\ty\t3\tz",
        ), 2)


class BenfordAnalyzerInputsTest(SimpleTestCase):
    def test_empty_input(self):
        analyzer = BenfordAnalyzer.create_from_string("")
        self.assertEqual(analyzer.total_occurences, 0)

    def test_invalid_inputs(self):
        analyzer_1 = BenfordAnalyzer.create_from_string("a")
        self.assertEqual(analyzer_1.total_occurences, 0)
        self.assertTrue(analyzer_1.has_errors)

        # No digits at all.
        analyzer_2 = BenfordAnalyzer.create_from_string("a\nb\nc")
        self.assertEqual(analyzer_2.total_occurences, 0)
        self.assertTrue(analyzer_2.has_errors)
        self.assertTrue(analyzer_2.error_count, 3)
        self.assertTrue(analyzer_2.error_rows, {0, 1, 2})

        # Rows with some errors
        analyzer_2 = BenfordAnalyzer.create_from_string("a\n1\nc")
        self.assertEqual(analyzer_2.total_occurences, 1)
        self.assertEqual(analyzer_2.get_occurences_for_digit(1), 1)
        self.assertTrue(analyzer_2.has_errors)
        self.assertEqual(analyzer_2.error_count, 2)
        self.assertSetEqual(analyzer_2.error_rows, {0, 2})

        # Test with empty lines
        analyzer_3 = BenfordAnalyzer.create_from_string("a\n\nb\n\n\n\n")
        self.assertEqual(analyzer_3.total_occurences, 0)
        self.assertTrue(analyzer_3.has_errors)
        self.assertSetEqual(analyzer_3.error_rows, {0, 1, 2, 3, 4, 5})

    def test_csv_inputs(self):
        analyzer_1 = BenfordAnalyzer.create_from_string("a\t1\nb\t2\nc\t3\nd\t123")
        self.assertEqual(analyzer_1.total_occurences, 4)
        self.assertEqual(analyzer_1.get_occurences_for_digit(1), 2)
        self.assertEqual(analyzer_1.get_percentage_for_digit(1), Decimal('50'))
        self.assertFalse(analyzer_1.has_errors)

    def test_valid_inputs(self):
        analyzer_1 = BenfordAnalyzer.create_from_string("1")
        self.assertEqual(analyzer_1.total_occurences, 1)
        self.assertFalse(analyzer_1.has_errors)
