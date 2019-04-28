from cone.app import root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_user_acl
from cone.ugm.layout import UGMLayout
from cone.ugm.model.user import User
from node.ext.ldap.ugm._api import User as LDAPUser
import unittest


class TestModelUser(unittest.TestCase):
    layer = testing.ugm_layer

    def test_user(self):
        # User node
        users = root['users']
        user = users['uid0']
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.name, 'uid0')

        # Properties
        self.assertTrue(isinstance(user.properties, Properties))

        # Metadata
        md = user.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'user_node')
        self.assertEqual(md.description, 'user_node_description')

        # Layout
        layout = user.layout
        self.assertTrue(isinstance(layout, UGMLayout))

        # Backend user node is available at ``model``
        self.assertTrue(isinstance(user.model, LDAPUser))

        # Attributes of the user are wrapped
        self.assertEqual(sorted(user.attrs.items()), [
            ('cn', 'cn0'),
            ('mail', 'uid0@groupOfNames_10_10.com'),
            ('rdn', 'uid0'),
            ('sn', 'sn0'),
            ('userPassword', 'secret0')
        ])

        # ACL
        self.assertEqual(user.__acl__, ugm_user_acl)
