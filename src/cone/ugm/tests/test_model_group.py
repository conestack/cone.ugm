from cone.app import root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.model.group import Group
from node.ext.ugm.interfaces import IGroup
import unittest


class TestModelGroup(unittest.TestCase):
    layer = testing.ugm_layer

    @testing.principals(
        groups={
            'group_1': {},
        })
    def test_group(self):
        # Group node
        groups = root['groups']
        group = groups['group_1']
        self.assertTrue(isinstance(group, Group))
        self.assertEqual(group.name, 'group_1')

        # Properties
        self.assertTrue(isinstance(group.properties, Properties))

        # Metadata
        md = group.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'group_node')
        self.assertEqual(md.description, 'group_node_description')

        # UGM backend group node is available at ``model``
        self.assertTrue(IGroup.providedBy(group.model))

        # Attributes of the group are wrapped
        self.assertTrue(group.attrs is group.model.attrs)

        # ACL
        self.assertEqual(group.__acl__, ugm_default_acl)
