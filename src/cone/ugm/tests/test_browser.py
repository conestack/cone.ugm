from cone.ugm import browser
from cone.ugm.testing import ugm_layer
import os
import unittest


def np(path):
    return path.replace('/', os.path.sep)


class TestBrowser(unittest.TestCase):
    layer = ugm_layer

    def test_cone_ugm_resources(self):
        resources_ = browser.cone_ugm_resources
        self.assertTrue(resources_.directory.endswith(np('/static')))
        self.assertEqual(resources_.name, 'cone.ugm-ugm')
        self.assertEqual(resources_.path, 'ugm')

        scripts = resources_.scripts
        self.assertEqual(len(scripts), 1)

        self.assertTrue(scripts[0].directory.endswith(np('/static')))
        self.assertEqual(scripts[0].path, 'ugm')
        self.assertEqual(scripts[0].file_name, 'cone.ugm.min.js')
        self.assertTrue(os.path.exists(scripts[0].file_path))

        styles = resources_.styles
        self.assertEqual(len(styles), 1)

        self.assertTrue(styles[0].directory.endswith(np('/static')))
        self.assertEqual(styles[0].path, 'ugm')
        self.assertEqual(styles[0].file_name, 'cone.ugm.min.css')
        self.assertTrue(os.path.exists(styles[0].file_path))
