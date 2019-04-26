from cone.app import root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.layout import UGMLayout
from cone.ugm.model.groups import Group
from cone.ugm.model.groups import Groups
from node.ext.ldap.ugm._api import Groups as LDAPGroups
from node.tests import NodeTestCase


class TestModelGroups(NodeTestCase):
    layer = testing.ugm_layer

    def test_groups(self):
        # Groups container
        groups = root['groups']
        self.assertTrue(isinstance(groups, Groups))
        self.assertEqual(groups.name, 'groups')

        # Properties
        self.assertTrue(isinstance(groups.properties, Properties))

        # Metadata
        md = groups.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'groups_node')
        self.assertEqual(md.description, 'groups_node_description')

        # Layout
        layout = groups.layout
        self.assertTrue(isinstance(layout, UGMLayout))

        # Iter groups
        self.assertEqual(len([x for x in groups]), 12)

        # Inexistent child
        self.expect_error(KeyError, groups.__getitem__, 'inexistent')

        # Children are group application nodes
        group = groups['group0']
        self.assertTrue(isinstance(group, Group))

        # If group gets deleted, it's not deleted from the underlying backend,
        # this is needed for invalidation
        del groups['group0']
        self.assertTrue(isinstance(groups['group0'], Group))

        backend = groups.backend
        self.assertTrue(isinstance(backend, LDAPGroups))
        self.assertTrue(backend is groups.backend)
        groups.invalidate()
        self.assertFalse(backend is groups.backend)

        # ACL
        self.assertEqual(groups.__acl__, ugm_default_acl)
