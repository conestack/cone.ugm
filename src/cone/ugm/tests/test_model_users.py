from cone.app import get_root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.model.user import User
from cone.ugm.model.users import Users
from node.ext.ugm.interfaces import IUsers
from node.tests import NodeTestCase
from unittest import mock


class ModelUsersTests:
    @testing.principals(
        users={
            'user_1': {},
            'user_2': {},
        }
    )
    def test_users(self):
        # Users container
        root = get_root()
        users = root['users']
        self.assertTrue(isinstance(users, Users))
        self.assertEqual(users.name, 'users')

        # Properties
        self.assertTrue(isinstance(users.properties, Properties))

        # Metadata
        md = users.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'users_node')
        self.assertEqual(md.description, 'users_node_description')

        # Iter users
        self.assertEqual(len([x for x in users]), 2)

        # Inexistent child
        self.expectError(KeyError, users.__getitem__, 'inexistent')

        # Children are user application nodes
        user = users['user_1']
        self.assertTrue(isinstance(user, User))

        # Check UGM backend
        backend = users.backend
        self.assertTrue(IUsers.providedBy(backend))

        # Check invalidate
        self.assertTrue(backend is users.backend)
        users.invalidate()
        self.assertFalse(backend is users.backend)

        # ACL
        self.assertEqual(users.__acl__, ugm_default_acl)

    def test_call_persists_backend(self):
        users = get_root()['users']
        backend = mock.Mock()
        with mock.patch.object(Users, 'backend', backend):
            users()
        backend.assert_called_once_with()

    def test_iter_failing_backend(self):
        users = get_root()['users']
        backend = mock.MagicMock()
        backend.__iter__.side_effect = Exception('Backend not available')
        with mock.patch.object(Users, 'backend', backend):
            with self.assertLogs('cone.ugm', level='ERROR') as logs:
                self.assertEqual([name for name in users], [])
        self.assertEqual(logs.output, ['ERROR:cone.ugm:Backend not available'])

    def test_getitem_backend_attribute_error(self):
        users = get_root()['users']
        backend = mock.MagicMock()
        backend.__getitem__.side_effect = AttributeError('user_1')
        with mock.patch.object(Users, 'backend', backend):
            err = self.expectError(KeyError, users.__getitem__, 'user_1')
        self.assertEqual(str(err), "'user_1'")


class TestModelUsers(NodeTestCase, ModelUsersTests):
    layer = testing.ugm_layer
