from cone.app import root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden


class TestBrowserGroups(TileTestCase):
    layer = testing.ugm_layer

    def test_content_tile(self):
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
        expected = '<div class="column left_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={
            'manager': ['manager']
        })
    def test_rightcolumn_tile(self):
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
        expected = '<div class="column right_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={
            'manager': ['manager']
        })
    def test_columnlisting_tile(self):
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
