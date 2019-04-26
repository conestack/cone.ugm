from cone.app import root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.exceptions import HTTPForbidden
from pyramid.view import render_view_to_response
from webob.response import Response
import json


def dummy_principals(fn):
    def wrapper(self):
        users = root['users']
        groups = root['groups']
        users.backend.create('uid99', sn='Uid99', cn='Uid99')
        users.backend()
        groups.backend.create('group99')
        groups.backend()
        try:
            fn(self, users, groups)
        finally:
            users.invalidate()
            groups.invalidate()
            try:
                del users.backend['uid99']
                users.backend()
            except Exception:
                # ignore, uid99 already deleted
                pass
            try:
                del groups.backend['group99']
                groups.backend()
            except Exception:
                # ignore, group99 already deleted
                pass
    return wrapper


class TestBrowserActions(TileTestCase):
    layer = testing.ugm_layer

    @dummy_principals
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
            'message': "u'uid100'",
            'success': False
        })

        self.assertEqual(group.model.member_ids, ['uid99'])

    @dummy_principals
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
            'message': "u'uid100'",
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

    @dummy_principals
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
            'message': "u'group100'",
            'success': False
        })

        self.assertEqual(user.model.group_ids, ['group99'])

    @dummy_principals
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
            'message': "u'group100'",
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

    @dummy_principals
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

        request.params['id'] = 'group99'
        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "Deleted user 'uid99' from database.",
            'success': True
        })

        with self.layer.authenticated('admin'):
            res = render_view_to_response(user, request, name='delete_item')
        self.assertEqual(json.loads(res.text), {
            'message': "u'uid99'",
            'success': False
        })

        self.assertEqual(group.model.users, [])

    @dummy_principals
    def test_delete_group_action(self, users, groups):
        #group = groups['group99']

        request = self.layer.new_request(type='json')
        """
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                group,
                request,
                name='delete_item'
            )
        """

"""
Test DeleteGroupAction::

    >>> layer.login('viewer')

    >>> group = groups['group99']
    >>> render_view_to_response(group, request, name='delete_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: delete_group_action failed 
    permission check

    >>> layer.login('admin')

    >>> res = render_view_to_response(group, request, name='delete_item')
    >>> res.body
    '{"message": "Deleted group from database", "success": true}'

    >>> res = render_view_to_response(group, request, name='delete_item')
    >>> res.body
    '{"message": "u\'group99\'", "success": false}'

    >>> groups.keys()
    [u'group0', u'group1', u'group2', u'group3', u'group4', u'group5', 
    u'group6', u'group7', u'group8', u'group9', u'admin_group_1', 
    u'admin_group_2']

    >>> layer.logout()

"""