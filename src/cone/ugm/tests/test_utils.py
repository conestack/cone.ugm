from cone.app import get_root
from cone.app.ugm import ugm_backend
from cone.ugm import testing
from cone.ugm.settings import GeneralSettings
from cone.ugm.utils import general_settings
from node.ext.ugm.interfaces import IUgm
import unittest


class TestUtilsBase(object):

    def test_general_settings(self):
        root = get_root()
        settings = general_settings(root)
        self.assertTrue(isinstance(settings, GeneralSettings))
        self.assertEqual(settings.name, 'ugm_general')

    def test_ugm_backend(self):
        backend = ugm_backend.ugm
        self.assertTrue(IUgm.providedBy(backend))

        self.assertTrue(backend is ugm_backend.ugm)
        ugm_backend.initialize()
        self.assertFalse(backend is ugm_backend.ugm)


class TestUtils(unittest.TestCase, TestUtilsBase):
    layer = testing.ugm_layer
