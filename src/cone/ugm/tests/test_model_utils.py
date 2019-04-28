from cone.app import root
from cone.app.ugm import ugm_backend
from cone.ugm import testing
from cone.ugm.model.settings import GeneralSettings
from cone.ugm.model.utils import ugm_general
from node.ext.ldap.ugm._api import Ugm
import unittest


class TestModelUtils(unittest.TestCase):
    layer = testing.ugm_layer

    def test_utils(self):
        general_settings = ugm_general(root)
        self.assertTrue(isinstance(general_settings, GeneralSettings))
        self.assertEqual(general_settings.name, 'ugm_general')

        self.assertEqual(ugm_backend.name, 'ldap')

        backend = ugm_backend.ugm
        self.assertTrue(isinstance(backend, Ugm))
        self.assertEqual(backend.name, 'ldap_ugm')

        self.assertTrue(backend is ugm_backend.ugm)
        ugm_backend.initialize()
        self.assertFalse(backend is ugm_backend.ugm)
