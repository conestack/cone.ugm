from cone.app import root
from cone.app.model import AppSettings
from cone.app.ugm import ugm_backend
from cone.ugm import testing
from cone.ugm.model.settings import GroupsSettings
from cone.ugm.model.settings import ServerSettings
from cone.ugm.model.settings import UsersSettings
from node.base import OrderedNode
from node.ext.ldap.properties import LDAPProps
from node.ext.ldap.properties import LDAPServerProperties
from node.ext.ldap.ugm._api import GroupsConfig
from node.ext.ldap.ugm._api import Ugm
from node.ext.ldap.ugm._api import UsersConfig
import unittest


class TestModelSettings(unittest.TestCase):
    layer = testing.ugm_layer

    def test_settings(self):
        # Dummy settings container
        settings = OrderedNode()
        settings['ugm_server'] = ServerSettings()
        settings['ugm_users'] = UsersSettings()
        settings['ugm_groups'] = GroupsSettings()

        # LDAP props
        props = settings['ugm_server'].ldap_props
        self.assertEqual(props.uri, 'ldap://127.0.0.1:12345')
        self.assertEqual(props.user, 'cn=Manager,dc=my-domain,dc=com')
        self.assertEqual(props.password, 'secret')

        md = settings['ugm_server'].metadata
        self.assertEqual(md.title, 'ldap_props_node')
        self.assertEqual(md.description, 'ldap_props_node_description')

        # LDAP users config
        ucfg = settings['ugm_users'].ldap_ucfg
        self.assertEqual(
            ucfg.baseDN,
            'ou=users,ou=groupOfNames_10_10,dc=my-domain,dc=com'
        )
        self.assertEqual(sorted(ucfg.attrmap.items()), [
            ('cn', 'cn'),
            ('id', 'uid'),
            ('jpegPhoto', 'jpegPhoto'),
            ('login', 'uid'),
            ('mail', 'mail'),
            ('rdn', 'uid'),
            ('sn', 'sn'),
            ('userPassword', 'userPassword')
        ])
        self.assertEqual(ucfg.scope, 1)
        self.assertEqual(ucfg.queryFilter, '')
        self.assertEqual(
            sorted(ucfg.objectClasses),
            ['inetOrgPerson', 'organizationalPerson', 'person', 'top']
        )

        md = settings['ugm_users'].metadata
        self.assertEqual(md.title, 'user_settings_node')
        self.assertEqual(md.description, 'user_settings_node_description')

        # LDAP groups config
        gcfg = settings['ugm_groups'].ldap_gcfg
        self.assertEqual(
            gcfg.baseDN,
            'ou=groups,ou=groupOfNames_10_10,dc=my-domain,dc=com'
        )
        self.assertEqual(sorted(gcfg.attrmap.items()), [
            ('id', 'cn'),
            ('rdn', 'cn')
        ])
        self.assertEqual(gcfg.scope, 1)
        self.assertEqual(gcfg.queryFilter, '')
        self.assertEqual(gcfg.objectClasses, ['groupOfNames'])

        md = settings['ugm_groups'].metadata
        self.assertEqual(md.title, 'group_settings_node')
        self.assertEqual(md.description, 'group_settings_node_description')

        # LDAP connectivity tests
        props = LDAPProps(
            uri='ldap://127.0.0.1:12346/',
            user='',
            password='',
            cache=False,
        )

        settings['ugm_server']._ldap_props = props
        self.assertFalse(settings['ugm_server'].ldap_connectivity)
        self.assertFalse(settings['ugm_users'].ldap_users_container_valid)
        self.assertFalse(settings['ugm_groups'].ldap_groups_container_valid)

        settings['ugm_server']._ldap_props = self.layer['props']
        settings['ugm_users']._ldap_ucfg = self.layer['ucfg']
        settings['ugm_groups']._ldap_gcfg = self.layer['gcfg']
        self.assertTrue(settings['ugm_server'].ldap_connectivity)
        self.assertTrue(settings['ugm_users'].ldap_users_container_valid)
        self.assertTrue(settings['ugm_groups'].ldap_groups_container_valid)

        # Settings are written on ``__call__``. At the moment all settings are
        # in one file, so calling either ucfg, gcfg or props writes all of them
        settings['ugm_server']()

        # Test invalidate
        settings = root['settings']
        self.assertTrue(isinstance(settings, AppSettings))

        props = settings['ugm_server'].ldap_props
        self.assertTrue(isinstance(props, LDAPServerProperties))

        ucfg = settings['ugm_users'].ldap_ucfg
        self.assertTrue(isinstance(ucfg, UsersConfig))

        gcfg = settings['ugm_groups'].ldap_gcfg
        self.assertTrue(isinstance(gcfg, GroupsConfig))

        backend = ugm_backend.ugm
        self.assertTrue(isinstance(backend, Ugm))
        self.assertTrue(backend is ugm_backend.ugm)

        settings = root['settings']
        props = settings['ugm_server'].ldap_props
        ucfg = settings['ugm_users'].ldap_ucfg
        gcfg = settings['ugm_groups'].ldap_gcfg

        self.assertTrue(props is settings['ugm_server'].ldap_props)
        self.assertTrue(ucfg is settings['ugm_users'].ldap_ucfg)
        self.assertTrue(gcfg is settings['ugm_groups'].ldap_gcfg)

        settings['ugm_server'].invalidate()
        self.assertFalse(backend is ugm_backend.ugm)
        self.assertFalse(props is settings['ugm_server'].ldap_props)
        self.assertFalse(ucfg is settings['ugm_users'].ldap_ucfg)
        self.assertFalse(gcfg is settings['ugm_groups'].ldap_gcfg)

        # Cleanup. Reset backend
        settings['ugm_server']._ldap_props = self.layer['props']
        settings['ugm_users']._ldap_ucfg = self.layer['ucfg']
        settings['ugm_groups']._ldap_gcfg = self.layer['gcfg']
