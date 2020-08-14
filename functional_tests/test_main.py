from django.test import LiveServerTestCase
from django.urls import resolve
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from benford.views import DashboardView


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
        self.browser.get('http://127.0.0.1:8000')
        self.assertEqual('Frank Benford\'s Law Project', self.browser.title)
        self.assertEqual(resolve('/').func.__name__, DashboardView.as_view().__name__)
