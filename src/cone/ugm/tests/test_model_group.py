from cone.app import root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.layout import UGMLayout
from cone.ugm.model.group import Group
from node.ext.ldap.ugm._api import Group as LDAPGroup
import unittest


class TestModelGroup(unittest.TestCase):
    layer = testing.ugm_layer

    def test_group(self):
        # Group node
        groups = root['groups']
        group = groups['group0']
        self.assertTrue(isinstance(group, Group))
        self.assertEqual(group.name, 'group0')

        # Properties
        self.assertTrue(isinstance(group.properties, Properties))

        # Metadata
        md = group.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'group_node')
        self.assertEqual(md.description, 'group_node_description')

        # Layout
        layout = group.layout
        self.assertTrue(isinstance(layout, UGMLayout))

        # Backend group node is available at ``model``
        self.assertTrue(isinstance(group.model, LDAPGroup))

        # Attributes of the group are wrapped
        self.assertEqual(sorted(group.attrs.items()), [
            ('member', [u'cn=nobody']),
            ('rdn', u'group0')
        ])

        # ACL
        self.assertEqual(group.__acl__, ugm_default_acl)
