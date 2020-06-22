from cone.app import root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_default_acl
from cone.ugm.model.user import User
from cone.ugm.model.users import Users
from node.ext.ugm.interfaces import IUsers
from node.tests import NodeTestCase


class TestModelUsers(NodeTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        users={
            'user_1': {},
            'user_2': {},
        })
    def test_users(self):
        # Users container
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
        self.expect_error(KeyError, users.__getitem__, 'inexistent')

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
