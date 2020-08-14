from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


class MainViewTest(LiveServerTestCase):
    def setUp(self):
        self.selenium = WebDriver()
        super(MainViewTest, self).setUp()
        
    def tearDown(self) -> None:
        self.selenium.quit()
        super(MainViewTest, self).tearDown()

    def test_home_page(self):
        browser = self.selenium
        browser.get('http://127.0.0.1:8000')
        self.assertEqual('Frank Benford\'s Law Project', browser.title)
