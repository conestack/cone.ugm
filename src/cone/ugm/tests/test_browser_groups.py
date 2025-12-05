from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden


class BrowserGroupsTests(object):

    def test_content_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/groups/login"'
        res = render_tile(groups, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={
            'manager': ['manager']
        })
    def test_leftcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            groups,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'leftcolumn')
        expected = '<div class="card column left_column">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={
            'manager': ['manager']
        })
    def test_rightcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            groups,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'rightcolumn')
        expected = '<div class="card column right_column bg-primary-100">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={
            'manager': ['manager']
        })
    def test_columnlisting_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            groups,
            request,
            'columnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'columnlisting')
        expected = '<div class="columnlisting leftbatchsensitiv"'
        self.assertTrue(res.find(expected) > -1)


class TestBrowserGroups(TileTestCase, BrowserGroupsTests):
    layer = testing.ugm_layer
