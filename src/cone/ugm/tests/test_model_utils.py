from cone.app import root
from cone.app.ugm import ugm_backend
from cone.ugm import testing
from cone.ugm.model.settings import GeneralSettings
from cone.ugm.model.utils import general_settings
from node.ext.ldap.ugm._api import Ugm
import unittest


class TestModelUtils(unittest.TestCase):
    layer = testing.ugm_layer

    def test_general_settings(self):
        settings = general_settings(root)
        self.assertTrue(isinstance(settings, GeneralSettings))
        self.assertEqual(settings.name, 'ugm_general')

    def test_ugm_backend(self):
        self.assertEqual(ugm_backend.name, 'ldap')

        backend = ugm_backend.ugm
        self.assertTrue(isinstance(backend, Ugm))
        self.assertEqual(backend.name, 'ldap_ugm')

        self.assertTrue(backend is ugm_backend.ugm)
        ugm_backend.initialize()
        self.assertFalse(backend is ugm_backend.ugm)
