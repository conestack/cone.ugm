from cone.app import get_root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.model.groups import Group
from cone.ugm.model.groups import Groups
from node.ext.ugm.interfaces import IGroups
from node.tests import NodeTestCase
from unittest import mock


class ModelGroupsTests:
    @testing.principals(
        groups={
            'group_1': {},
            'group_2': {},
        }
    )
    def test_groups(self):
        # Groups container
        root = get_root()
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

        # Iter groups
        self.assertEqual(len([x for x in groups]), 2)

        # Inexistent child
        self.expectError(KeyError, groups.__getitem__, 'inexistent')

        # Children are group application nodes
        group = groups['group_1']
        self.assertTrue(isinstance(group, Group))

        # Check UGM backend
        backend = groups.backend
        self.assertTrue(IGroups.providedBy(backend))

        # Check invalidate
        self.assertTrue(backend is groups.backend)
        groups.invalidate()
        self.assertFalse(backend is groups.backend)

        # ACL
        self.assertEqual(groups.__acl__, ugm_default_acl)

    def test_call_persists_backend(self):
        groups = get_root()['groups']
        backend = mock.Mock()
        with mock.patch.object(Groups, 'backend', backend):
            groups()
        backend.assert_called_once_with()

    def test_iter_failing_backend(self):
        groups = get_root()['groups']
        backend = mock.MagicMock()
        backend.__iter__.side_effect = Exception('Backend not available')
        with mock.patch.object(Groups, 'backend', backend):
            with self.assertLogs('cone.ugm', level='ERROR') as logs:
                self.assertEqual([name for name in groups], [])
        self.assertEqual(logs.output, ['ERROR:cone.ugm:Backend not available'])

    def test_getitem_backend_attribute_error(self):
        groups = get_root()['groups']
        backend = mock.MagicMock()
        backend.__getitem__.side_effect = AttributeError('group_1')
        with mock.patch.object(Groups, 'backend', backend):
            err = self.expectError(KeyError, groups.__getitem__, 'group_1')
        self.assertEqual(str(err), "'group_1'")


class TestModelGroups(NodeTestCase, ModelGroupsTests):
    layer = testing.ugm_layer
