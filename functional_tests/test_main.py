import os
import time

from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import resolve
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from benford.views import DashboardView, DatasetUploadView


class MainViewTest(LiveServerTestCase):
    def setUp(self):
        options = Options()
        options.add_argument('--headless')
        self.browser = WebDriver(options=options)
        super(MainViewTest, self).setUp()

    def tearDown(self) -> None:
        self.browser.quit()
        super(MainViewTest, self).tearDown()

    def test_dashboard_page(self):
        # Run the page.
        self.browser.get('http://127.0.0.1:8000/')
        self.assertEqual('Frank Benford\'s Law Project', self.browser.title)
        self.assertEqual(resolve('/').func.__name__, DashboardView.as_view().__name__)

        # Table with created datasets.
        table = self.browser.find_element_by_id('table-datasets')

        # There is an upload button that redirects us to the form page.
        button = self.browser.find_element_by_link_text('Upload new dataset')
        button.click()

        # We expect to navigate to upload form page
        element = WebDriverWait(self.browser, 5).until(
            expected_conditions.presence_of_element_located(
                (By.ID, 'form-upload-dataset')))
        self.assertEqual(self.browser.current_url, 'http://127.0.0.1:8000/upload/')

    def test_dataset_upload_form(self):
        # I navigate to the upload form page
        self.browser.get('http://127.0.0.1:8000/upload/')
        self.assertEqual(resolve('/upload/').func.__name__, DatasetUploadView.as_view().__name__)

        form = self.browser.find_element_by_id('form-upload-dataset')

        # There should be a submit button.
        submit_button_1 = self.browser.find_element_by_id('id_submit')

        # If we click the submit button right after page load...
        submit_button_1.click()

        # ...then we get an error.
        WebDriverWait(self.browser, 3).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, 'li'),
                'Please provide either file or raw data.'))

        # So we upload our sample real-world data file.
        upload_field = self.browser.find_element_by_id('id_data_file')
        upload_field.send_keys(os.path.join(settings.BASE_DIR, 'benford/tests/sample_data/census_2009b'))

        # Extra title can be added to the form (not required)
        title_field = self.browser.find_element_by_id('id_title')
        title_field.send_keys('My first dataset')

        # The form should be submitted
        submit_button_2 = self.browser.find_element_by_id('id_submit')
        submit_button_2.click()
        time.sleep(3)

        # And we land on a dataset page.
        self.assertIn('My first dataset', self.browser.title)
