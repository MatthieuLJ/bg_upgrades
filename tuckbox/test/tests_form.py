from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import Select, WebDriverWait
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
#      ----------                                       v                                  |
#     |Paper size|                                /          \                             |
#     |is changed|----+                          /            \                            |
#      ----------     |  +----------------+     /Are all fields\       +--------------+    |
#                     +->|Hide "won't fit"|--->  valid numbers  ------>|Remove preview|----+
#                     |  +----------------+     \and not empty?/       +--------------+    |
#     --------------  |                          \            /                            |
#    |Page is loaded|-+                           \          /                             |
#     --------------                                    |                                  |
#                                                       v                                  |
#                                              +----------------+                          |
#                                              |Generate preview|                          |
#                                              +----------------+                          |
#     ------------                                      |                                  |
#    |PDF is being|     +-----------------+             v                                  |
#    |  generated | --->|Show the progress|-----+    /     \                               |
#     ------------      +-----------------+     |   /Does it\         +----------------+   |
#                                               +-->  fit?    ------->|Show "won't fit"|---+
#    ---------------      +-----------------+   |   \       /         +----------------+   |
#   |PDF is received|---->|Hide the progress|---|    \     /                               v
#    ---------------      +-----------------+           |                          +-----------------+
#                                                       +------------------------->|Check to enable  |
#                                                                                  |the submit button|
#                                                                                  +-----------------+
#                                                                               Submit button is enabled if:
#                                                                             * All the numeric fields are valid and not empty
#                                                                             * It fits
#                                                                             * There is no request already ongoing

# Useful links:
#  https://selenium-python.readthedocs.io/index.html

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

    def set_text_field(self, field, text):
        field.clear()
        field.send_keys(text)
        field.send_keys(Keys.TAB)

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

        # Progress should be hidden
        progress = self.selenium.find_element_by_id("id_progress_container")
        self.assertFalse(progress.is_displayed())

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

        self.set_text_field(height_field, "abc")
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        self.set_text_field(height_field, "-2")
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        self.set_text_field(height_field, "10$1")
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        self.set_text_field(height_field, "101")
        self.assertEqual(height_field.value_of_css_property("color"), "rgba(0, 0, 0, 1)")

        paper_select = Select(self.selenium.find_element_by_id('id_paper_size'))
        paper_select.select_by_visible_text('Custom')
        custom_paper_height = self.selenium.find_element_by_id("id_paper_height")

        self.set_text_field(custom_paper_height, "abc")
        self.assertEqual(custom_paper_height.value_of_css_property("color"), "rgba(255, 0, 0, 1)")
        
        self.set_text_field(custom_paper_height, "-2")
        self.assertEqual(custom_paper_height.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        self.set_text_field(custom_paper_height, "10$1")
        self.assertEqual(custom_paper_height.value_of_css_property("color"), "rgba(255, 0, 0, 1)")

        self.set_text_field(custom_paper_height, "101")
        self.assertEqual(custom_paper_height.value_of_css_property("color"), "rgba(0, 0, 0, 1)")

    def test_fit(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/tuck/'))

        height_field = self.selenium.find_element_by_id("id_height")
        width_field = self.selenium.find_element_by_id("id_width")
        depth_field = self.selenium.find_element_by_id("id_depth")
        paper_select = Select(self.selenium.find_element_by_id('id_paper_size'))
        paper_select.select_by_visible_text('A4')
        wont_fit_label = self.selenium.find_element_by_id("id_wont_fit")
        two_openings = self.selenium.find_element_by_id("id_two_openings").find_element_by_xpath('..')

        # initial conditions
        self.assertEqual(wont_fit_label.value_of_css_property("display"), "none")
        
        # basic
        self.set_text_field(height_field, "200")
        self.set_text_field(width_field, "100")
        self.set_text_field(depth_field, "100")
        WebDriverWait(self.selenium, 5).until(EC.visibility_of(wont_fit_label))
        self.assertNotEqual(wont_fit_label.value_of_css_property("display"), "none")

        self.set_text_field(height_field, "40")
        self.set_text_field(width_field, "30")
        self.set_text_field(depth_field, "20")
        WebDriverWait(self.selenium, 5).until_not(EC.visibility_of(wont_fit_label))
        self.assertEqual(wont_fit_label.value_of_css_property("display"), "none")

        # check with layout adjustments (this pattern would only fit in landscape mode)
        self.set_text_field(height_field, "100")
        self.set_text_field(width_field, "60")
        self.set_text_field(depth_field, "40")
        WebDriverWait(self.selenium, 5).until_not(EC.visibility_of(wont_fit_label))
        self.assertEqual(wont_fit_label.value_of_css_property("display"), "none")

        # check with two openings
        self.set_text_field(height_field, "205")
        self.set_text_field(width_field, "60")
        self.set_text_field(depth_field, "30")
        WebDriverWait(self.selenium, 5).until_not(EC.visibility_of(wont_fit_label))
        self.assertEqual(wont_fit_label.value_of_css_property("display"), "none")

        two_openings.click()
        WebDriverWait(self.selenium, 5).until(EC.visibility_of(wont_fit_label))
        self.assertNotEqual(wont_fit_label.value_of_css_property("display"), "none")


# TODO:
#  - Check when the submit button is activated
#  - Check the custom paper fields appear when that option is selected
#  - Check the clear file fields
        



