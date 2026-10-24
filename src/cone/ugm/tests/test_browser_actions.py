from cone.app import get_root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.events import GroupDeletedEvent
from cone.ugm.events import UserDeletedEvent
from cone.ugm.tests.fixtures import local_management_enabled
from cone.ugm.tests.fixtures import local_manager_principals
from cone.ugm.tests.fixtures import register_event_handler
from pyramid.exceptions import HTTPForbidden
from pyramid.view import render_view_to_response
from webob.multidict import MultiDict
import json


class BrowserActionsTests:
    @testing.principals(
        users={'user_1': {}, 'viewer': {}, 'editor': {}},
        groups={'group_1': {}},
        roles={'viewer': ['viewer'], 'editor': ['editor']},
    )
    def test_group_add_user_action(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden, render_view_to_response, group, request, name='add_item'
            )

        request.params['id'] = 'user_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(
            json.loads(res.text),
            {'message': "Added user 'user_1' to group 'group_1'.", 'success': True},
        )

        request.params['id'] = 'user_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'user_2'") > -1)

        self.assertEqual(group.model.member_ids, ['user_1'])

    @testing.principals(
        users={'user_1': {}, 'viewer': {}, 'editor': {}},
        groups={'group_1': {}},
        membership={'group_1': ['user_1']},
        roles={'viewer': ['viewer'], 'editor': ['editor']},
    )
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
                name='remove_item',
            )

        request.params['id'] = 'user_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'user_2'") > -1)

        request.params['id'] = 'user_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(
            json.loads(res.text),
            {'message': "Removed user 'user_1' from group 'group_1'.", 'success': True},
        )

        self.assertEqual(group.model.users, [])

    @testing.principals(
        users={'user_1': {}, 'viewer': {}, 'editor': {}},
        groups={'group_1': {}},
        roles={'viewer': ['viewer'], 'editor': ['editor']},
    )
    def test_user_add_to_group_action(self):
        root = get_root()
        users = root['users']
        user = users['user_1']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden, render_view_to_response, user, request, name='add_item'
            )

        request.params['id'] = 'group_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(
            json.loads(res.text),
            {'message': "Added user 'user_1' to group 'group_1'.", 'success': True},
        )

        request.params['id'] = 'group_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'group_2'") > -1)

        self.assertEqual(user.model.group_ids, ['group_1'])

    @testing.principals(
        users={'user_1': {}, 'viewer': {}, 'editor': {}},
        groups={'group_1': {}},
        membership={'group_1': ['user_1']},
        roles={'viewer': ['viewer'], 'editor': ['editor']},
    )
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
                name='remove_item',
            )

        request.params['id'] = 'group_2'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'group_2'") > -1)

        request.params['id'] = 'group_1'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(
            json.loads(res.text),
            {'message': "Removed user 'user_1' from group 'group_1'.", 'success': True},
        )

        self.assertEqual(user.model.groups, [])

    @testing.principals(
        users={'user_1': {}, 'viewer': {}, 'admin': {}},
        groups={'group_1': {}},
        membership={'group_1': ['user_1']},
        roles={'viewer': ['viewer'], 'admin': ['admin']},
    )
    def test_delete_user_action(self):
        root = get_root()
        groups = root['groups']
        users = root['users']

        group = groups['group_1']
        user = users['user_1']

        events_called = []

        def on_user_deleted(event):
            events_called.append('UserDeletedEvent')

        register_event_handler(self, UserDeletedEvent, on_user_deleted)

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='delete_item',
            )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')

        self.assertEqual(
            json.loads(res.text),
            {'message': "Deleted user 'user_1' from database.", 'success': True},
        )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'user_1'") > -1)

        self.assertEqual(group.model.users, [])
        self.assertTrue('UserDeletedEvent' in events_called)

    @testing.principals(
        users={'viewer': {}, 'admin': {}},
        groups={'group_1': {}},
        roles={'viewer': ['viewer'], 'admin': ['admin']},
    )
    def test_delete_group_action(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']

        request = self.layer.new_request(type='json')

        events_called = []

        def on_group_deleted(event):
            events_called.append('GroupDeletedEvent')

        register_event_handler(self, GroupDeletedEvent, on_group_deleted)

        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='delete_item',
            )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(group, request, name='delete_item')
        self.assertEqual(
            json.loads(res.text),
            {'message': 'Deleted group from database', 'success': True},
        )

        with self.layer.authenticated('admin'):
            res = render_view_to_response(group, request, name='delete_item')
        json_res = json.loads(res.text)
        self.assertFalse(json_res['success'])
        self.assertTrue(json_res['message'].find("'group_1'") > -1)

        self.assertEqual(groups.keys(), [])
        self.assertTrue('GroupDeletedEvent' in events_called)

    def _multi_id_request(self, *ids):
        request = self.layer.new_request(type='json')
        request.params = MultiDict(request.params)
        for id_ in ids:
            request.params.add('id[]', id_)
        return request

    @testing.principals(
        users={'user_1': {}, 'editor': {}},
        groups={'group_1': {}, 'group_2': {}},
        roles={'editor': ['editor']},
    )
    def test_user_add_to_groups_action(self):
        user = get_root()['users']['user_1']
        request = self._multi_id_request('group_1', 'group_2')
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(
            json.loads(res.text),
            {
                'message': "Added user 'user_1' to group 'group_1, group_2'.",
                'success': True,
            },
        )
        self.assertEqual(sorted(user.model.group_ids), ['group_1', 'group_2'])

    @testing.principals(
        users={'user_1': {}, 'editor': {}},
        groups={'group_1': {}, 'group_2': {}},
        membership={'group_1': ['user_1'], 'group_2': ['user_1']},
        roles={'editor': ['editor']},
    )
    def test_user_remove_from_groups_action(self):
        user = get_root()['users']['user_1']
        request = self._multi_id_request('group_1', 'group_2')
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(
            json.loads(res.text),
            {
                'message': "Removed user 'user_1' from group 'group_1, group_2'.",
                'success': True,
            },
        )
        self.assertEqual(user.model.group_ids, [])

    @testing.principals(
        users={'user_1': {}, 'user_2': {}, 'editor': {}},
        groups={'group_1': {}},
        roles={'editor': ['editor']},
    )
    def test_group_add_users_action(self):
        group = get_root()['groups']['group_1']
        request = self._multi_id_request('user_1', 'user_2')
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(
            json.loads(res.text),
            {
                'message': "Added user 'user_1, user_2' to group 'group_1'.",
                'success': True,
            },
        )
        self.assertEqual(sorted(group.model.member_ids), ['user_1', 'user_2'])

    @testing.principals(
        users={'user_1': {}, 'user_2': {}, 'editor': {}},
        groups={'group_1': {}},
        membership={'group_1': ['user_1', 'user_2']},
        roles={'editor': ['editor']},
    )
    def test_group_remove_users_action(self):
        group = get_root()['groups']['group_1']
        request = self._multi_id_request('user_1', 'user_2')
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(
            json.loads(res.text),
            {
                'message': "Removed user 'user_1, user_2' from group 'group_1'.",
                'success': True,
            },
        )
        self.assertEqual(group.model.member_ids, [])

    def _render_action(self, model, login, name, id_):
        request = self.layer.new_request(type='json')
        request.params['id'] = id_
        with self.layer.authenticated(login):
            res = render_view_to_response(model, request, name=name)
        return json.loads(res.text)

    @local_manager_principals
    @local_management_enabled
    def test_user_add_to_group_action_local_manager(self):
        user = get_root()['users']['managed_user']
        res = self._render_action(user, 'local_manager', 'add_item', 'managed_group_0')
        self.assertEqual(
            res,
            {
                'message': "Added user 'managed_user' to group 'managed_group_0'.",
                'success': True,
            },
        )
        self.assertEqual(
            sorted(user.model.group_ids), ['managed_group_0', 'managed_group_1']
        )

    @local_manager_principals
    @local_management_enabled
    def test_user_add_to_group_action_local_manager_group_not_managed(self):
        user = get_root()['users']['managed_user']
        res = self._render_action(user, 'local_manager', 'add_item', 'managed_group_2')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed adding user 'managed_user' to group 'managed_group_2'. "
                    'Manage membership denied for target group.'
                ),
                'success': False,
            },
        )
        self.assertEqual(user.model.group_ids, ['managed_group_1'])

    @local_manager_principals
    @local_management_enabled
    def test_user_add_to_group_action_local_manager_user_not_managed(self):
        # The editor role grants ``manage_membership`` on users outside the
        # managed groups too.
        user = get_root()['users']['unmanaged_user']
        res = self._render_action(user, 'local_editor', 'add_item', 'managed_group_0')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed adding user 'unmanaged_user' to group 'managed_group_0'. "
                    'Manage membership denied for user.'
                ),
                'success': False,
            },
        )
        self.assertEqual(user.model.group_ids, ['managed_group_2'])

    @local_manager_principals
    @local_management_enabled
    def test_user_remove_from_group_action_local_manager(self):
        user = get_root()['users']['managed_user']
        groups = get_root()['groups']
        groups['managed_group_0'].model.add('managed_user')
        groups()
        res = self._render_action(user, 'local_manager', 'remove_item', 'managed_group_0')
        self.assertEqual(
            res,
            {
                'message': "Removed user 'managed_user' from group 'managed_group_0'.",
                'success': True,
            },
        )
        self.assertEqual(user.model.group_ids, ['managed_group_1'])

    @local_manager_principals
    @local_management_enabled
    def test_user_remove_from_group_action_local_manager_group_not_managed(self):
        user = get_root()['users']['managed_user']
        res = self._render_action(user, 'local_manager', 'remove_item', 'managed_group_2')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'managed_user' from group "
                    "'managed_group_2'. Manage membership denied for target group."
                ),
                'success': False,
            },
        )

    @local_manager_principals
    @local_management_enabled
    def test_user_remove_from_group_action_local_manager_default_group(self):
        user = get_root()['users']['managed_user']
        res = self._render_action(user, 'local_manager', 'remove_item', 'managed_group_1')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'managed_user' from group "
                    "'managed_group_1'. Target group is default group of user."
                ),
                'success': False,
            },
        )
        self.assertEqual(user.model.group_ids, ['managed_group_1'])

    @local_manager_principals
    @local_management_enabled
    def test_user_remove_from_group_action_local_manager_user_not_managed(self):
        # The editor role grants ``manage_membership`` on users outside the
        # managed groups too.
        user = get_root()['users']['unmanaged_user']
        res = self._render_action(user, 'local_editor', 'remove_item', 'managed_group_0')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'unmanaged_user' from group "
                    "'managed_group_0'. Manage membership denied for user."
                ),
                'success': False,
            },
        )

    @local_manager_principals
    @local_management_enabled
    def test_group_add_user_action_local_manager(self):
        group = get_root()['groups']['managed_group_0']
        res = self._render_action(group, 'local_manager', 'add_item', 'managed_user')
        self.assertEqual(
            res,
            {
                'message': "Added user 'managed_user' to group 'managed_group_0'.",
                'success': True,
            },
        )
        self.assertEqual(group.model.member_ids, ['managed_user'])

    @local_manager_principals
    @local_management_enabled
    def test_group_add_user_action_local_manager_user_not_managed(self):
        group = get_root()['groups']['managed_group_0']
        res = self._render_action(group, 'local_manager', 'add_item', 'unmanaged_user')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed adding user 'unmanaged_user' to group 'managed_group_0'. "
                    'Manage membership denied for user.'
                ),
                'success': False,
            },
        )
        self.assertEqual(group.model.member_ids, [])

    @local_manager_principals
    @local_management_enabled
    def test_group_add_user_action_local_manager_group_not_managed(self):
        # The editor role grants ``manage_membership`` on groups outside the
        # managed ones too.
        group = get_root()['groups']['managed_group_2']
        res = self._render_action(group, 'local_editor', 'add_item', 'managed_user')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed adding user 'managed_user' to group 'managed_group_2'. "
                    'Manage membership denied for target group.'
                ),
                'success': False,
            },
        )
        self.assertEqual(group.model.member_ids, ['unmanaged_user'])

    @local_manager_principals
    @local_management_enabled
    def test_group_remove_user_action_local_manager(self):
        group = get_root()['groups']['managed_group_0']
        group.model.add('managed_user')
        group()
        res = self._render_action(group, 'local_manager', 'remove_item', 'managed_user')
        self.assertEqual(
            res,
            {
                'message': "Removed user 'managed_user' from group 'managed_group_0'.",
                'success': True,
            },
        )
        self.assertEqual(group.model.member_ids, [])

    @local_manager_principals
    @local_management_enabled
    def test_group_remove_user_action_local_manager_user_not_managed(self):
        group = get_root()['groups']['managed_group_0']
        res = self._render_action(group, 'local_manager', 'remove_item', 'unmanaged_user')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'unmanaged_user' from group "
                    "'managed_group_0'. Manage membership denied for user."
                ),
                'success': False,
            },
        )

    @local_manager_principals
    @local_management_enabled
    def test_group_remove_user_action_local_manager_default_group(self):
        group = get_root()['groups']['managed_group_1']
        res = self._render_action(group, 'local_manager', 'remove_item', 'managed_user')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'managed_user' from group "
                    "'managed_group_1'. Target group is default group of user."
                ),
                'success': False,
            },
        )
        self.assertEqual(group.model.member_ids, ['managed_user'])

    @local_manager_principals
    @local_management_enabled
    def test_group_remove_user_action_local_manager_group_not_managed(self):
        # The editor role grants ``manage_membership`` on groups outside the
        # managed ones too.
        group = get_root()['groups']['managed_group_2']
        res = self._render_action(group, 'local_editor', 'remove_item', 'unmanaged_user')
        self.assertEqual(
            res,
            {
                'message': (
                    "Failed removing user 'unmanaged_user' from group "
                    "'managed_group_2'. Manage membership denied for target group."
                ),
                'success': False,
            },
        )


class TestBrowserActions(TileTestCase, BrowserActionsTests):
    layer = testing.ugm_layer
