from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden


class BrowserUsersTests(object):

    def test_content_tile(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/users/login"'
        res = render_tile(users, request, 'content')
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
        users = root['users']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            users,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'leftcolumn')
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
        users = root['users']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            users,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'rightcolumn')
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
        users = root['users']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            users,
            request,
            'columnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'columnlisting')
        expected = '<div class="columnlisting leftbatchsensitiv"'
        self.assertTrue(res.find(expected) > -1)


class TestBrowserUsers(TileTestCase, BrowserUsersTests):
    layer = testing.ugm_layer
