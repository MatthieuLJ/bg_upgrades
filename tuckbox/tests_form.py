from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

#  ------------------
# | Dimension field  |                                /    \
# |    is changed    |-+                             /      \
#  ------------------  |   +----------------+       /Empty or\      +-------------------+
#                      +-->|Hide "won't fit"|------>  valid   ----->|Make field text red|--+
#                      |   +----------------+       \ input? /      +-------------------+  |
#                      |                             \      /                              |
#  ------------------  |                              \    /                               |
# |Custom paper size |-+                                |                                  |
# |   is changed     |                                  v                                  |
#  ------------------                        +---------------------+                       |
#                                            |Make field text black|                       |
#                                            +---------------------+                       |
#                                                       |                                  |
#     +----------+                                      v                                  |
#     |Paper size|                                /          \                             |
#     |is changed|----+                          /            \                            |
#     +----------+    |  +----------------+     /Are all fields\       +--------------+    |
#                     +->|Hide "won't fit"|--->  valid numbers  ------>|Remove preview|----+
#                     |  +----------------+     \and not empty?/       +--------------+    |
#    +--------------+ |                          \            /                            |
#    |Page is loaded|-+                           \          /                             |
#    +--------------+                                   |                                  |
#                                                       v                                  |
#                                              +----------------+                          |
#                                              |Generate preview|                          |
#                                              +----------------+                          |
#    +------------+                                     |                                  |
#    |PDF is being|     +-----------------+             v                                  |
#    |  generated | --->|Show the throbber|-----+    /     \                               |
#    +------------+     +-----------------+     |   /Does it\         +----------------+   |
#                                               +-->  fit?    ------->|Show "won't fit"|---+
#   +---------------+     +-----------------+   |   \       /         +----------------+   |
#   |PDF is received|---->|Hide the throbber|---|    \     /                               v
#   +---------------+     +-----------------+           |                          +-----------------+
#                                                       +------------------------->|Check to enable  |
#                                                                                  |the submit button|
#                                                                                  +-----------------+
#                                                                               Submit button is enabled if:
#                                                                             * All the numeric fields are valid and not empty
#                                                                             * It fits
#                                                                             * There is no request already ongoing


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

    def test_atLoadTime(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))

        # Won't fit label should be hidden
        wont_fit = self.selenium.find_element_by_id("id_wont_fit")
        self.assertFalse(wont_fit.is_displayed())

        # Throbber should be hidden
        throbber = self.selenium.find_element_by_id("id_throbber")
        self.assertFalse(throbber.is_displayed())

        # Custom paper size fields should be hidden and values should be loaded with some default
        custom_paper_height = self.selenium.find_element_by_id("id_paper_height")
        self.assertFalse(custom_paper_height.is_displayed())
        val = self.selenium.execute_script("return document.getElementById('id_paper_height').value;")
        self.assertNotEqual(val, "")

        custom_paper_width = self.selenium.find_element_by_id("id_paper_width")
        self.assertFalse(custom_paper_width.is_displayed())
        val = self.selenium.execute_script("return document.getElementById('id_paper_width').value;")
        self.assertNotEqual(val, "")

        # Submit button should be disabled
        submit_button = self.selenium.find_element_by_id("id_submit")
        self.assertFalse(submit_button.is_enabled())

    def test_badEntriesInNumField(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))

        height_field = self.selenium.find_element_by_id("id_height")
        height_field.clear()
        height_field.send_keys("abc")
        height_field.send_keys(Keys.TAB)
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        height_field.clear()
        height_field.send_keys("-2")
        height_field.send_keys(Keys.TAB)
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        height_field.clear()
        height_field.send_keys("10$1")
        height_field.send_keys(Keys.TAB)
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        height_field.clear()
        height_field.send_keys("101")
        height_field.send_keys(Keys.TAB)
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(0, 0, 0, 1)")


# TODO:
#  - Wont_fit is shown with some parameters
#  - Check when the submit button is activated
#  - Check the custom paper fields appear when that option is selected
#  - Check the clear file fields
        



