from django.test import LiveServerTestCase
from django.urls import resolve
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from benford.views import DashboardView, UploadDatasetView


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
        self.browser.get('http://127.0.0.1:8000')
        self.assertEqual('Frank Benford\'s Law Project', self.browser.title)
        self.assertEqual(resolve('/').func.__name__, DashboardView.as_view().__name__)

        # Table with created datasets.
        table = self.browser.find_element_by_id('table-datasets')

        # There is an upload button that redirects me to the form page.
        button = self.browser.find_element_by_link_text('Upload new dataset')

    def test_dataset_upload_form(self):
        # I navigate to the upload form page
        self.browser.get('http://127.0.0.1:8000/upload')
        self.assertEqual(resolve('/upload').func.__name__, UploadDatasetView.as_view().__name__)
        form = self.browser.find_element_by_id('form-upload-dataset')

        # Dataset field must be filled in or a file must be uploaded.

        # Extra title can be added to the form (not required)

        # The form should be submitted

