from decimal import Decimal

from django.test.testcases import TestCase

from benford.models import Dataset, SignificantDigit


class DatasetTest(TestCase):
    def setUp(self):
        pass

    def test_basics(self):
        dataset = Dataset.objects.create(title='Census_2009b')
        self.assertEqual(Dataset.objects.count(), 1)

        # Ensure there can only be one significant digit entry for a given dataset.
        self.assertIn(('dataset', 'digit'), SignificantDigit._meta.unique_together)

        # We store how many times a significant/leading number occured in a set.
        SignificantDigit.objects.create(dataset=dataset, digit=1, occurences=100)
        SignificantDigit.objects.create(dataset=dataset, digit=2, occurences=90)
        SignificantDigit.objects.create(dataset=dataset, digit=3, occurences=80)
        SignificantDigit.objects.create(dataset=dataset, digit=4, occurences=70)
        SignificantDigit.objects.create(dataset=dataset, digit=5, occurences=60)
        SignificantDigit.objects.create(dataset=dataset, digit=6, occurences=50)
        SignificantDigit.objects.create(dataset=dataset, digit=7, occurences=40)
        SignificantDigit.objects.create(dataset=dataset, digit=8, occurences=30)
        SignificantDigit.objects.create(dataset=dataset, digit=9, occurences=20)

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
