import os
import unittest

from lib.browser.drive import BrowserDriver
from lib.browser.drive import DriverError


class TestBrowserDriver(unittest.TestCase):

    def _test_data_folder(self):
        module_folder = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(module_folder, 'data')

    #def test_yaml(self):
    #    import yaml
    #    data = {
    #        'urls': [
    #            dict(url='http://something', title='Google'),
    #            dict(url='http://else', title='Yahoo'),
    #        ]
    #    }
    #    with open('/home/patrick/repo/temp/temp.yaml', 'w') as f:
    #        yaml.dump(data, f, default_flow_style=False)

    #def test_driver(self):
    #    BrowserDriver('csw_web', self._test_data_folder())

    #def test_driver_missing_url(self):
    #    with self.assertRaises(DriverError) as cm:
    #        BrowserDriver('csw_web_missing_url', self._test_data_folder())
    #    self.assertIn(
    #        "should have a 'url'",
    #        cm.exception.value
    #    )

    #def test_driver_missing_title(self):
    #    with self.assertRaises(DriverError) as cm:
    #        BrowserDriver('csw_web_missing_title', self._test_data_folder())
    #    self.assertIn(
    #        "should have a 'title'",
    #        cm.exception.value
    #    )

    #def test_browser_driver(self):
    #    driver = BrowserDriver('csw_web', self._test_data_folder())
    #    driver.test()
    #    driver.close()

    #def test_browser_driver_timeout(self):
    #    driver = BrowserDriver('csw_web_invalid_title', self._test_data_folder())
    #    with self.assertRaises(DriverError) as cm:
    #        driver.test()
    #    self.assertIn(
    #        "Time out waiting for page",
    #        cm.exception.value
    #    )
    #    driver.close()