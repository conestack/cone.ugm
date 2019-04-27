from cone.app import root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from pyramid.httpexceptions import HTTPForbidden


class TestBrowserSettings(TileTestCase):
    layer = testing.ugm_layer

    def test_settings(self):
        server_settings = root['settings']['ugm_server']
        users_settings = root['settings']['ugm_users']
        groups_settings = root['settings']['ugm_groups']

        request = self.layer.new_request()

        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            server_settings,
            request,
            'content'
        )
        self.expectError(
            HTTPForbidden,
            render_tile,
            users_settings,
            request,
            'content'
        )
        self.expectError(
            HTTPForbidden,
            render_tile,
            groups_settings,
            request,
            'content'
        )

        # Form tiles raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                server_settings,
                request,
                'editform'
            )
            self.expectError(
                HTTPForbidden,
                render_tile,
                users_settings,
                request,
                'editform'
            )
            self.expectError(
                HTTPForbidden,
                render_tile,
                groups_settings,
                request,
                'editform'
            )

        # Authenticate and render tiles
        with self.layer.authenticated('manager'):
            res = render_tile(server_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm_server/edit"'
        self.assertTrue(res.find(expected) > -1)

        with self.layer.authenticated('manager'):
            res = render_tile(users_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm_users/edit"'
        self.assertTrue(res.find(expected) > -1)

        with self.layer.authenticated('manager'):
            res = render_tile(groups_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm_groups/edit"'
        self.assertTrue(res.find(expected) > -1)
