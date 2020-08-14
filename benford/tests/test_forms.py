from decimal import Decimal

from django.test.testcases import TestCase

from benford.core import BenfordAnalyzer
from benford.forms import DatasetUploadForm
from benford.tests.common import RAW_DATA_SAMPLE_1, RAW_DATA_SAMPLE_2


class DatasetUploadFormTest(TestCase):
    def test_empty_form(self):
        form = DatasetUploadForm()

        # Empty form should not be valid.
        self.assertFalse(form.is_valid())

    def test_form_with_raw_data(self):
        payload = {
            'data_raw': RAW_DATA_SAMPLE_1,
        }
        form = DatasetUploadForm(payload)

        # Ensure the form is "clean".
        self.assertListEqual(list(form.errors), [])
        self.assertTrue(form.is_valid())

        benford_analyzer = BenfordAnalyzer.create_from_form(form)
        self.assertIsInstance(benford_analyzer, BenfordAnalyzer)
        self.assertEqual(len(benford_analyzer._occurences), len(benford_analyzer.percentages))

        self.assertDictEqual(
            benford_analyzer.occurences,
            {1: 5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1})

        self.assertDictEqual(
            benford_analyzer.percentages,
            {1: 50, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10})

    def test_form_with_census_2009b_sample(self):
        payload = {
            'data_raw': RAW_DATA_SAMPLE_2,
            'relevant_column': 2,  # Third column contains relevant data.
            'has_header': True,  # We will ignore first row in given dataset.
        }
        form = DatasetUploadForm(payload)
        self.assertTrue(form.is_valid())

        benford_analyzer = BenfordAnalyzer.create_from_form(form)
        self.assertEqual(benford_analyzer.total_occurences, 19)
        self.assertFalse(benford_analyzer.has_errors)

    def test_form_with_file_data(self):
        pass
