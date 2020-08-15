import re

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

    def test_multiple_datasets(self):
        dataset_1 = Dataset.objects.create(title='A')
        dataset_2 = Dataset.objects.create(title='B')
        dataset_3 = Dataset.objects.create(title='C')
        self.assertEqual(Dataset.objects.count(), 3)
