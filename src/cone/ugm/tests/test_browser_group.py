from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.model.group import Group
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound


class TestBrowserGroup(TileTestCase):
    layer = testing.ugm_layer

    def test_content_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group5']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/groups/group5/login"'
        res = render_tile(group, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    def test_leftcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group5']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'leftcolumn')
        expected = '<div class="column left_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    def test_rightcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group5']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'rightcolumn')
        expected = '<div class="column right_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    def test_columnlisting_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group5']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'columnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'columnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/uid5">'
        )
        self.assertTrue(res.find(expected) > -1)

    def test_allcolumnlisting_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group5']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'allcolumnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'allcolumnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/uid1">'
        )
        self.assertTrue(res.find(expected) > -1)

        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/uid6">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals()
    def test_add_group(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()
        request.params['factory'] = 'group'

        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                groups,
                request,
                'add'
            )

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        expected = '<form action="http://example.com/groups/add"'
        self.assertTrue(res.find(expected) > -1)

        request.params['groupform.id'] = ''
        request.params['groupform.principal_roles'] = []
        request.params['action.groupform.save'] = '1'

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        expected = '<div class="text-danger">No group_id defined</div>'
        self.assertTrue(res.find(expected) > -1)

        request.params['groupform.id'] = 'group99'

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertEqual(sorted(groups.keys()), [
            'admin_group_1', 'admin_group_2', 'group0', 'group1', 'group2',
            'group3', 'group4', 'group5', 'group6', 'group7', 'group8',
            'group9', 'group99'
        ])

        group = groups['group99']
        self.assertTrue(isinstance(group, Group))

    @testing.principals(groups={'group99': {}})
    def test_edit_group(self):
        root = get_root()
        groups = root['groups']
        group = groups['group99']
        request = self.layer.new_request()

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'edit')
        expected = '<form action="http://example.com/groups/group99/edit"'
        self.assertTrue(res.find(expected) > -1)
