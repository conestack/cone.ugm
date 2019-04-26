from cone.app import root
from cone.app.ugm import ugm_backend
from cone.ugm import testing
from cone.ugm.model.settings import GroupsSettings
from cone.ugm.model.settings import ServerSettings
from cone.ugm.model.settings import UsersSettings
from cone.ugm.model.utils import ugm_groups
from cone.ugm.model.utils import ugm_server
from cone.ugm.model.utils import ugm_users
from node.ext.ldap.ugm._api import Ugm
import unittest


class TestModelUtils(unittest.TestCase):
    layer = testing.ugm_layer

    def test_utils(self):
        server_settings = ugm_server(root)
        self.assertTrue(isinstance(server_settings, ServerSettings))
        self.assertEqual(server_settings.name, 'ugm_server')

        users_settings = ugm_users(root)
        self.assertTrue(isinstance(users_settings, UsersSettings))
        self.assertEqual(users_settings.name, 'ugm_users')

        groups_settings = ugm_groups(root)
        self.assertTrue(isinstance(groups_settings, GroupsSettings))
        self.assertEqual(groups_settings.name, 'ugm_groups')

        self.assertEqual(ugm_backend.name, 'ldap')

        backend = ugm_backend.ugm
        self.assertTrue(isinstance(backend, Ugm))
        self.assertEqual(backend.name, 'ldap_ugm')

        self.assertTrue(backend is ugm_backend.ugm)
        ugm_backend.initialize()
        self.assertFalse(backend is ugm_backend.ugm)
