from django.test.testcases import TestCase

from benford.forms import DatasetUploadForm
from benford.tests.common import RAW_DATA_SAMPLE_1


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

    def test_form_with_file_data(self):
        pass
