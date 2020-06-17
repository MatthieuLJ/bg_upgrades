from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ViewTestCase(TestCase):
    def test_tuckPage(self):
        c = Client()
        response = c.get('/tuck/')

        self.assertEqual(200, response.status_code)

    def test_redirectFromRoot(self):
        c = Client()
        response = c.get('/', follow=True)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], 'tuck/')

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        #cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_customPaperSizesHidden(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))
        custom_paper_height_field = self.selenium.find_element_by_name("paper_height")
        self.assertFalse(custom_paper_height_field.is_displayed())
        custom_paper_width_field = self.selenium.find_element_by_name("paper_width")
        self.assertFalse(custom_paper_width_field.is_displayed())
        height_field = self.selenium.find_element_by_name("height")
        self.assertTrue(height_field.is_displayed())

    def test_show3Dmodel(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))
        
        model_container = self.selenium.find_element_by_id("image_preview")
        children = model_container.find_elements_by_xpath(".//*")
        self.assertEqual(0, len(children))

        height_field = self.selenium.find_element_by_name("height")
        height_field.send_keys("40")
        width_field = self.selenium.find_element_by_name("width")
        width_field.send_keys("30")
        depth_field = self.selenium.find_element_by_name("depth")
        depth_field.send_keys("20")
        height_field.send_keys("")

        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='image_preview']/*")))

        children = model_container.find_elements_by_xpath(".//*")
        self.assertEqual(1, len(children))

    def test_findWontFit(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))
        
        wont_fit = self.selenium.find_element_by_id("id_wont_fit")
        self.assertFalse(wont_fit.is_displayed())

# TODO:
#  - Wont_fit is shown with some parameters
#  - Check when the submit button is activated
#  - Check the custom paper fields appear when that option is selected
#  - Check the clear file fields
        



