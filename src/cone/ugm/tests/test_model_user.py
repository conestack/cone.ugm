from cone.app import get_root
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.ugm import testing
from cone.ugm import ugm_user_acl
from cone.ugm.model.user import User
from datetime import datetime
from node.ext.ugm.interfaces import IUser
from pyramid.authorization import Allow
from types import SimpleNamespace
import unittest


class ModelUserTests:
    @testing.principals(
        users={
            'user_1': {},
        }
    )
    def test_user(self):
        # User node
        root = get_root()
        users = root['users']
        user = users['user_1']
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.name, 'user_1')

        # Properties
        self.assertTrue(isinstance(user.properties, Properties))

        # Metadata
        md = user.metadata
        self.assertTrue(isinstance(md, Metadata))
        self.assertEqual(md.title, 'user_node')
        self.assertEqual(md.description, 'user_node_description')

        # UGM backend user node is available at ``model``
        self.assertTrue(IUser.providedBy(user.model))

        # Attributes of the user are wrapped
        self.assertTrue(user.attrs is user.model.attrs)

        # ACL
        self.layer.new_request()
        self.assertEqual(user.__acl__, ugm_user_acl)

        with self.layer.authenticated('user_1'):
            self.assertEqual(
                user.__acl__,
                [(Allow, 'user_1', ['change_own_password'])] + ugm_user_acl,
            )

    def test_expires_unsupported_by_backend(self):
        user = User(object(), 'user_1', None)
        self.assertIsNone(user.expires)

    def test_expires_set_on_backend_user(self):
        model = SimpleNamespace(expires=None)
        user = User(model, 'user_1', None)
        expires = datetime(2030, 1, 1)
        user.expires = expires
        self.assertEqual(model.expires, expires)
        self.assertEqual(user.expires, expires)


class TestModelUser(unittest.TestCase, ModelUserTests):
    layer = testing.ugm_layer
