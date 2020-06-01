from cone.app import get_root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import render_view_to_response
import json


class TestBrowserRemote(TileTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        users={
            'viewer': {},
            'manager': {},
            'user_1': {}
        },
        groups={
            'group_1': {},
            'group_2': {},
        },
        roles={
            'viewer': ['viewer'],
            'manager': ['manager'],
        })
    def test_add_user(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request(type='json')

        # Need add permission
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                users,
                request,
                name='remote_add_user'
            )

        # No id given
        request.params['id'] = ''
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'No user ID given.',
            'success': False
        })

        # Existent id given
        request.params['id'] = 'user_1'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'User with given ID already exists.',
            'success': False
        })

        # Add minimal valid user
        request.params['id'] = 'user_2'
        request.params['attr.fullname'] = 'Sepp Unterwurzacher'
        request.params['attr.email'] = 'sepp.unterwurzacher@example.com'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Created user with ID 'user_2'.",
            'success': True
        })

        # Check new user
        user = users['user_2']

        self.assertEqual(user.attrs['fullname'], 'Sepp Unterwurzacher')
        self.assertEqual(user.attrs['email'], 'sepp.unterwurzacher@example.com')

        # This user has nor roles and is not member of a group
        self.assertEqual(user.model.roles, [])
        self.assertEqual(user.model.groups, [])

        # There was no password given, thus we cannot authenticate with this
        # user yet
        self.assertFalse(user.model.authenticate('secret'))

        user.model.passwd(None, 'secret')
        self.assertTrue(user.model.authenticate('secret'))

        # Create another user with initial password
        request.params['id'] = 'user_3'
        request.params['password'] = 'secret'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Created user with ID 'user_3'.",
            'success': True
        })

        user = users['user_3']
        self.assertTrue(user.model.authenticate('secret'))

        # Create user with initial roles. Message tells us if some of this
        # roles are not available
        request.params['id'] = 'user_4'
        request.params['password'] = 'secret'
        request.params['roles'] = 'editor,viewer,inexistent'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Role 'inexistent' given but inexistent. Created user with ID 'user_4'.",
            'success': True
        })

        # Create user with intial group membership. Message tells us if some of
        # this groups are not available
        request.params['id'] = 'user_5'
        request.params['password'] = 'secret'
        request.params['roles'] = 'editor,viewer,inexistent'
        request.params['groups'] = 'group_1,group_2,group_inexistent'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': (
                "Role 'inexistent' given but inexistent. Group 'group_inexistent' "
                "given but inexistent. Created user with ID 'user_5'."
            ),
            'success': True
        })

        # Check created user
        user = users['user_5']
        self.assertEqual(sorted(user.model.group_ids), ['group_1', 'group_2'])
        self.assertEqual(sorted(user.model.roles), ['editor', 'viewer'])
        self.assertTrue(user.model.authenticate('secret'))

    @testing.principals(
        users={
            'viewer': {},
            'manager': {},
            'user_1': {}
        },
        roles={
            'viewer': ['viewer'],
            'manager': ['manager'],
        })
    def test_delete_user(self):
        root = get_root()
        users = root['users']

        request = self.layer.new_request(type='json')

        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                users,
                request,
                name='remote_delete_user'
            )

        # No id given
        request.params['id'] = ''
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'No user ID given.',
            'success': False
        })

        # Inexistent id given
        request.params['id'] = 'user_2'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'User with given ID not exists.',
            'success': False
        })

        # Valid deletions
        request.params['id'] = 'user_1'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Deleted user with ID 'user_1\'.",
            'success': True
        })
