import os
import socket

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase, tag, override_settings
from django.urls import resolve
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from benford.analyzer import BenfordAnalyzer
from benford.models import Dataset
from benford.tests.test_forms import create_census_2009b_form
from benford.views import DashboardView, DatasetUploadView


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class MainViewTest(StaticLiveServerTestCase):
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.browser = webdriver.Remote(
            command_executor='http://selenium_hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_dashboard_page(self):
        # Run the page.
        self.browser.get(self.live_server_url)
        self.assertEqual('Frank Benford\'s Law Project', self.browser.title)
        self.assertEqual(resolve('/').func.__name__, DashboardView.as_view().__name__)

        # Table with created datasets.
        table = self.browser.find_elements_by_css_selector('#table-datasets')

        # There is an upload button that redirects us to the form page.
        button = self.browser.find_element_by_link_text('Upload new dataset')
        button.click()

        # We expect to navigate to upload form page
        element = WebDriverWait(self.browser, 5).until(
            expected_conditions.presence_of_element_located(
                (By.ID, 'form-upload-dataset')),
            message="No form with id='form-upload-dataset' available on the page.")
        self.assertEqual(self.browser.current_url, self.live_server_url + '/upload/')

    def test_dataset_upload_form(self):
        # I navigate to the upload form page
        self.browser.get(self.live_server_url + '/upload/')
        self.assertEqual(resolve('/upload/').func.__name__, DatasetUploadView.as_view().__name__)

        form = self.browser.find_element_by_id('form-upload-dataset')

        # There should be a submit button.
        submit_button_1 = self.browser.find_element_by_id('id_submit')

        # If we click the submit button right after page load...
        submit_button_1.click()

        # ...then we get an error.
        WebDriverWait(self.browser, 3).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 '//li[text()[contains(.,"Please provide either file or raw data.")]]')),
            message="There was no error message displayed from the form.")

        # So we upload our sample real-world data file.
        upload_field = self.browser.find_element_by_id('id_data_file')
        upload_field.send_keys(os.path.join(settings.BASE_DIR, 'benford/tests/sample_data/census_2009b'))

        # Extra title can be added to the form (not required)
        title_field = self.browser.find_element_by_id('id_title')
        title_field.send_keys('My first dataset')

        # The form should be submitted
        submit_button_2 = self.browser.find_element_by_id('id_submit')
        submit_button_2.click()

        # And we land on a dataset page.
        WebDriverWait(self.browser, 3).until(
            expected_conditions.title_contains('My first dataset'),
            message="Page title didn't change as expected. "
                    "It should contain 'My first dataset'.")

        h2 = self.browser.find_element_by_tag_name('h2')
        self.assertEqual(h2.text, 'Erroneous rows')

    def test_dataset_detail_page(self):
        # We create some dataset.
        analyzer = BenfordAnalyzer(occurences={
            1: 5735, 2: 3544, 3: 2341, 4: 1847, 5: 1559,
            6: 1370, 7: 1166, 8: 1042, 9: 903,
        }, title='My dataset')

        # And save it to database.
        dataset = analyzer.save()
        self.assertEqual(Dataset.objects.count(), 1)

        # Let's navigate to main page.
        self.browser.get(self.live_server_url)

        # We should see recently added datasets. Let's find ours.
        dataset_link = self.browser.find_element_by_link_text('My dataset')
        self.assertEqual(
            dataset_link.get_attribute('href'),
            self.live_server_url + dataset.get_absolute_url())

        # And we click on it!
        dataset_link.click()

        WebDriverWait(self.browser, 5).until(
            expected_conditions.presence_of_element_located(
                (By.ID, 'table-dataset-summary')))

        # We should see the page header.
        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertEqual(h1.text, 'My dataset')

        # Expect summary table...
        summary_table = self.browser.find_element_by_id('table-dataset-summary')

        # ...with a header.
        thead = summary_table.find_element_by_tag_name('thead')
        thead_ths = thead.find_elements_by_css_selector('th')
        self.assertEqual(len(thead_ths), 4)
        self.assertEqual(thead_ths[0].text, 'Digit')
        self.assertEqual(thead_ths[1].text, 'Occurences')
        self.assertEqual(thead_ths[2].text, 'Percent')
        self.assertEqual(thead_ths[3].text, 'Expected')

        # Since we have all 9 digits in our dataset, we expect 9 rows
        # in the table body.
        tbody = summary_table.find_element_by_tag_name('tbody')
        table_rows = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(len(table_rows), 9)

        tds = table_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(tds), 4)
        self.assertEqual(tds[0].text, '1')
        self.assertEqual(tds[1].text, '5735')
        self.assertEqual(tds[2].text, '29.4')
        self.assertEqual(tds[3].text, '30.1')

        # There should be a graph image on the page.
        graph_img = self.browser.find_element_by_xpath('//img[contains(@class, "graph")]')

    def test_browsing_data(self):
        form = create_census_2009b_form()
        self.assertTrue(form.is_valid())
        analyzer = BenfordAnalyzer.create_from_form(form)
        dataset: Dataset = analyzer.save()
        self.browser.get(self.live_server_url + dataset.get_absolute_url())

        browse_data_link = self.browser.find_element_by_xpath(
            '//a[text()[contains(.,"Browse data")]]')
        browse_data_link.click()

        WebDriverWait(self.browser, 3).until(
            expected_conditions.presence_of_element_located(
                (By.ID, 'table-dataset-rows')),
            message="There was no table with id=table-dataset-rows.")

        table = self.browser.find_element_by_id('table-dataset-rows')

        # There should be 100 data rows on the first page.
        self.assertEqual(
            len(table.find_elements_by_tag_name('tr')), 100)
