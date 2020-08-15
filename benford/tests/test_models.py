import re
from decimal import Decimal

from django.test.testcases import TestCase

from benford.models import Dataset, SignificantDigit


class DatasetTest(TestCase):
    def setUp(self):
        pass

    def test_title(self):
        dataset_without_title = Dataset.objects.create()
        self.assertEqual(dataset_without_title.display_title(), 'Untitled dataset')

        dataset_with_title = Dataset.objects.create(title='My title')
        self.assertEqual(dataset_with_title.display_title(), 'My title')

    def test_get_absolute_url(self):
        dataset = Dataset.objects.create(slug='abcdabcdef')
        self.assertEqual(dataset.get_absolute_url(), '/dataset/abcdabcdef/')

    def test_basics(self):
        dataset = Dataset.objects.create(title='Census_2009b')
        self.assertEqual(Dataset.objects.count(), 1)

        # Ensure that we have a unique identifier.
        self.assertTrue(len(dataset.slug), 10)
        self.assertIsNotNone(re.match(r'[a-z]{10}', dataset.slug))

        # Ensure there can only be one significant digit entry for a given dataset.
        self.assertIn(('dataset', 'digit'), SignificantDigit._meta.unique_together)

        # We store how many times a significant/leading number occured in a set.
        SignificantDigit.objects.create(dataset=dataset, digit=1, occurences=100, percentage=Decimal('18.5'))
        SignificantDigit.objects.create(dataset=dataset, digit=2, occurences=90, percentage=Decimal('16.7'))
        SignificantDigit.objects.create(dataset=dataset, digit=3, occurences=80, percentage=Decimal('14.8'))
        SignificantDigit.objects.create(dataset=dataset, digit=4, occurences=70, percentage=Decimal('13.0'))
        SignificantDigit.objects.create(dataset=dataset, digit=5, occurences=60, percentage=Decimal('11.1'))
        SignificantDigit.objects.create(dataset=dataset, digit=6, occurences=50, percentage=Decimal('9.3'))
        SignificantDigit.objects.create(dataset=dataset, digit=7, occurences=40, percentage=Decimal('7.4'))
        SignificantDigit.objects.create(dataset=dataset, digit=8, occurences=30, percentage=Decimal('5.6'))
        SignificantDigit.objects.create(dataset=dataset, digit=9, occurences=20, percentage=Decimal('3.6'))

        self.assertEqual(SignificantDigit.objects.count(), 9)

        # Count all records.
        self.assertEqual(dataset.count_records(), 540)

        # Calculate occurence percentages - how often a given digit occured
        # compared to other digits.
        significant_1 = SignificantDigit.objects.get(dataset=dataset, digit=1)
        self.assertEqual(significant_1.calculate_occurence_percentage(), Decimal('18.5'))

        significant_2 = SignificantDigit.objects.get(dataset=dataset, digit=2)
        self.assertEqual(significant_2.calculate_occurence_percentage(), Decimal('16.7'))

        significant_3 = SignificantDigit.objects.get(dataset=dataset, digit=3)
        self.assertEqual(significant_3.calculate_occurence_percentage(), Decimal('14.8'))

    def test_multiple_datasets(self):
        dataset_1 = Dataset.objects.create(title='A')
        dataset_2 = Dataset.objects.create(title='B')
        dataset_3 = Dataset.objects.create(title='C')
        self.assertEqual(Dataset.objects.count(), 3)
