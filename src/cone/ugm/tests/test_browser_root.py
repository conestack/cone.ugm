from cone.app import root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden


class TestBrowserRoot(TileTestCase):
    layer = testing.ugm_layer

    def test_content_tile(self):
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/login"'
        res = render_tile(root, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'editor': {},
        },
        roles={
            'editor': ['editor'],
        })
    def test_leftcolumn_tile(self):
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            root,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('editor'):
            res = render_tile(root, request, 'leftcolumn')
        expected = '<div class="column left_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'editor': {},
        },
        roles={
            'editor': ['editor'],
        })
    def test_rightcolumn_tile(self):
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            root,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('editor'):
            res = render_tile(root, request, 'rightcolumn')
        expected = '<div class="column right_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'editor': {},
        },
        roles={
            'editor': ['editor'],
        })
    def test_site_name_tile(self):
        request = self.layer.new_request()

        with self.layer.authenticated('editor'):
            self.assertEqual(render_tile(root, request, 'site'), 'SITENAME')
