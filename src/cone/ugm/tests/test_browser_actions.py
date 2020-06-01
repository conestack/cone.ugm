from cone.app import compat
from cone.app import get_root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.exceptions import HTTPForbidden
from pyramid.view import render_view_to_response
import json


class TestBrowserActions(TileTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        users={
            'user_1': {},
            'viewer': {},
            'editor': {}
        },
        groups={
            'group_1': {}
        },
        roles={
            'viewer': ['viewer'],
            'editor': ['editor']
        })
    def test_group_add_user_action(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='add_item'
            )

        request.params['id'] = 'user_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Added user 'user_1' to group 'group_1'.",
            'success': True
        })

        request.params['id'] = 'user_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'user_2'" if compat.IS_PY2 else "'user_2'",
            'success': False
        })

        self.assertEqual(group.model.member_ids, ['user_1'])

    @testing.principals(
        users={
            'user_1': {},
            'viewer': {},
            'editor': {}
        },
        groups={
            'group_1': {}
        },
        membership={
            'group_1': ['user_1']
        },
        roles={
            'viewer': ['viewer'],
            'editor': ['editor']
        })
    def test_group_remove_user_action(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='remove_item'
            )

        request.params['id'] = 'user_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'user_2'" if compat.IS_PY2 else "'user_2'",
            'success': False
        })

        request.params['id'] = 'user_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Removed user 'user_1' from group 'group_1'.",
            'success': True
        })

        self.assertEqual(group.model.users, [])

    @testing.principals(
        users={
            'user_1': {},
            'viewer': {},
            'editor': {}
        },
        groups={
            'group_1': {}
        },
        roles={
            'viewer': ['viewer'],
            'editor': ['editor']
        })
    def test_user_add_to_group_action(self):
        root = get_root()
        users = root['users']
        user = users['user_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='add_item'
            )

        request.params['id'] = 'group_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Added user 'user_1' to group 'group_1'.",
            'success': True
        })

        request.params['id'] = 'group_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'group_2'" if compat.IS_PY2 else "'group_2'",
            'success': False
        })

        self.assertEqual(user.model.group_ids, ['group_1'])

    @testing.principals(
        users={
            'user_1': {},
            'viewer': {},
            'editor': {}
        },
        groups={
            'group_1': {}
        },
        membership={
            'group_1': ['user_1']
        },
        roles={
            'viewer': ['viewer'],
            'editor': ['editor']
        })
    def test_user_remove_from_group_action(self):
        root = get_root()
        users = root['users']
        user = users['user_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='remove_item'
            )

        request.params['id'] = 'group_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'group_2'" if compat.IS_PY2 else "'group_2'",
            'success': False
        })

        request.params['id'] = 'group_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Removed user 'user_1' from group 'group_1'.",
            'success': True
        })

        self.assertEqual(user.model.groups, [])

    @testing.principals(
        users={
            'user_1': {},
            'viewer': {},
            'admin': {}
        },
        groups={
            'group_1': {}
        },
        membership={
            'group_1': ['user_1']
        },
        roles={
            'viewer': ['viewer'],
            'admin': ['admin']
        })
    def test_delete_user_action(self):
        root = get_root()
        groups = root['groups']
        users = root['users']

        group = groups['group_1']
        user = users['user_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='delete_item'
            )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Deleted user 'user_1' from database.",
            'success': True
        })

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'user_1'" if compat.IS_PY2 else "'user_1'",
            'success': False
        })

        self.assertEqual(group.model.users, [])

    @testing.principals(
        users={
            'viewer': {},
            'admin': {}
        },
        groups={
            'group_1': {}
        },
        roles={
            'viewer': ['viewer'],
            'admin': ['admin']
        })
    def test_delete_group_action(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='delete_item'
            )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(group, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Deleted group from database",
            'success': True
        })

        with self.layer.authenticated('admin'):
            res = render_view_to_response(group, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'group_1'" if compat.IS_PY2 else "'group_1'",
            'success': False
        })

        self.assertEqual(groups.keys(), [])
