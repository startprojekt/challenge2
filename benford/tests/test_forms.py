from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.utils import ErrorList
from django.test.testcases import TestCase

from benford.analyzer import BenfordAnalyzer
from benford.forms import DatasetUploadForm
from benford.models import DatasetRow, Dataset
from benford.tests.common import RAW_DATA_SAMPLE_1, RAW_DATA_SAMPLE_2


def create_census_2009b_form():
    with open('benford/tests/sample_data/census_2009b', 'rb') as uploaded_file:
        payload = {
            # We don't need to pass the 'relevant_column' parameter
            # since it will be detected automatically (first number).
            # 'relevant_column': 2,
            'has_header': True,
        }
        payload_files = {
            'data_file': SimpleUploadedFile(uploaded_file.name, uploaded_file.read()),
        }
    form = DatasetUploadForm(payload, payload_files)
    return form


class DatasetUploadFormTest(TestCase):
    def test_empty_form(self):
        form = DatasetUploadForm({})

        # Empty form should not be valid.
        self.assertFalse(form.is_valid())
        self.assertListEqual(
            form.non_field_errors(),
            ErrorList(['Please provide either file or raw data.']))

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

    def test_form_with_real_world_file_data(self):
        """
        This is form testing with the "real world" data provided in the challenge.
        """

        form = create_census_2009b_form()
        self.assertTrue(form.is_valid())
        self.assertListEqual(list(form.errors), [])

        benford_analyzer = BenfordAnalyzer.create_from_form(form)
        self.assertTrue(benford_analyzer.has_errors)

        # We found 2 erroneous rows in the dataset.
        self.assertEqual(len(benford_analyzer.error_rows), 2)

        # So the total count of valid rows would be:
        self.assertEqual(benford_analyzer.total_occurences, 19507)

        self.assertDictEqual(
            benford_analyzer.occurences, {
                1: 5735, 2: 3544, 3: 2341, 4: 1847, 5: 1559,
                6: 1370, 7: 1166, 8: 1042, 9: 903,
            })

        self.assertDictEqual(
            benford_analyzer.percentages, {
                1: Decimal('29.4'), 2: Decimal('18.2'), 3: Decimal('12.0'),
                4: Decimal('9.5'), 5: Decimal('8.0'), 6: Decimal('7.0'),
                7: Decimal('6.0'), 8: Decimal('5.3'), 9: Decimal('4.6'),
            })

    def test_dataset_rows(self):
        form = create_census_2009b_form()
        self.assertTrue(form.is_valid())

        benford_analyzer = BenfordAnalyzer.create_from_form(form)
        benford_analyzer.save()

        self.assertEqual(Dataset.objects.count(), 1)

        # Let's test saved rows.
        self.assertEqual(
            DatasetRow.objects.filter(
                dataset=benford_analyzer.dataset
            ).count(), 19510)

        # We should be able to retrieve erroneous rows.
        self.assertEqual(
            DatasetRow.objects.filter(
                dataset=benford_analyzer.dataset,
                has_error=True
            ).count(), 2)
