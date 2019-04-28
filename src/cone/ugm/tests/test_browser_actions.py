from cone.app import compat
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.exceptions import HTTPForbidden
from pyramid.view import render_view_to_response
import json


temp_users = {
    'uid99': {
        'sn': 'Uid99',
        'cn': 'Uid99'
    }
}
temp_groups = {
    'group99': {}
}


class TestBrowserActions(TileTestCase):
    layer = testing.ugm_layer

    @testing.temp_principals(users=temp_users, groups=temp_groups)
    def test_group_add_user_action(self, users, groups):
        group = groups['group99']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='add_item'
            )

        request.params['id'] = 'uid99'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Added user 'uid99' to group 'group99'.",
            'success': True
        })

        request.params['id'] = 'uid100'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'uid100'" if compat.IS_PY2 else "'uid100'",
            'success': False
        })

        self.assertEqual(group.model.member_ids, ['uid99'])

    @testing.temp_principals(users=temp_users, groups=temp_groups)
    def test_group_remove_user_action(self, users, groups):
        group = groups['group99']
        group.model.add('uid99')
        group.model()

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='remove_item'
            )

        request.params['id'] = 'uid100'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'uid100'" if compat.IS_PY2 else "'uid100'",
            'success': False
        })

        request.params['id'] = 'uid99'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(group, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Removed user 'uid99' from group 'group99'.",
            'success': True
        })

        self.assertEqual(group.model.users, [])

    @testing.temp_principals(users=temp_users, groups=temp_groups)
    def test_user_add_to_group_action(self, users, groups):
        user = users['uid99']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='add_item'
            )

        request.params['id'] = 'group99'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Added user 'uid99' to group 'group99'.",
            'success': True
        })

        request.params['id'] = 'group100'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='add_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'group100'" if compat.IS_PY2 else "'group100'",
            'success': False
        })

        self.assertEqual(user.model.group_ids, ['group99'])

    @testing.temp_principals(users=temp_users, groups=temp_groups)
    def test_user_remove_from_group_action(self, users, groups):
        group = groups['group99']
        group.model.add('uid99')
        group.model()

        user = users['uid99']

        request = self.layer.new_request(type='json')
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                user,
                request,
                name='remove_item'
            )

        request.params['id'] = 'group100'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'group100'" if compat.IS_PY2 else "'group100'",
            'success': False
        })

        request.params['id'] = 'group99'
        with self.layer.authenticated('editor'):
            res = render_view_to_response(user, request, name='remove_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Removed user 'uid99' from group 'group99'.",
            'success': True
        })

        self.assertEqual(user.model.groups, [])

    @testing.temp_principals(users=temp_users, groups=temp_groups)
    def test_delete_user_action(self, users, groups):
        group = groups['group99']
        group.model.add('uid99')
        group.model()

        user = users['uid99']

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
            'message': "Deleted user 'uid99' from database.",
            'success': True
        })

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'uid99'" if compat.IS_PY2 else "'uid99'",
            'success': False
        })

        self.assertEqual(group.model.users, [])

    @testing.temp_principals(groups=temp_groups)
    def test_delete_group_action(self, users, groups):
        group = groups['group99']

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
            'message': "u'group99'" if compat.IS_PY2 else "'group99'",
            'success': False
        })

        self.assertEqual(groups.keys(), [
            'group0', 'group1', 'group2', 'group3', 'group4', 'group5',
            'group6', 'group7', 'group8', 'group9', 'admin_group_1',
            'admin_group_2'
        ])
