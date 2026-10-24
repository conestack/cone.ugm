from cone.app import get_root
from cone.ugm import register_config
from cone.ugm import register_entry
from cone.ugm import testing
from cone.ugm.model.users import Users
from cone.ugm.settings import GeneralSettings
from unittest import mock
import os
import unittest


class TestInit(unittest.TestCase):
    layer = testing.ugm_layer

    def test_register_entry_skips_registered_entry_in_testrun(self):
        self.assertIn('users', get_root().factories)
        with mock.patch.dict(os.environ, {'TESTRUN_MARKER': '1'}):
            with mock.patch('cone.ugm._register_entry') as register:
                register_entry('users', Users)
        register.assert_not_called()

    def test_register_config_skips_registered_config_in_testrun(self):
        self.assertIn('ugm_general', get_root()['settings'].factories)
        with mock.patch.dict(os.environ, {'TESTRUN_MARKER': '1'}):
            with mock.patch('cone.ugm._register_config') as register:
                register_config('ugm_general', GeneralSettings)
        register.assert_not_called()
