from cone.app import get_root
from cone.app import root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.settings import GeneralSettingsForm
from cone.ugm.model.settings import ugm_cfg
from pyramid.httpexceptions import HTTPForbidden
import os


class TestBrowserSettings(TileTestCase):
    layer = testing.ugm_layer

    @testing.custom_config_path
    @testing.temp_directory
    def test_GeneralSettingsForm(self, tempdir):
        config_file = os.path.join(tempdir, 'ugm.xml')
        ugm_cfg.ugm_settings = config_file
        with open(config_file, 'w') as f:
            f.write('<properties></properties>')

        model = get_root()['settings']['ugm_general']
        request = self.layer.new_request()

        tile = GeneralSettingsForm()
        tile.model = model
        tile.request = request
        tile.prepare()

        form = tile.form
        self.assertEqual(form.keys(), [
            'users_heading',
            'users_account_expiration',
            'users_expires_attr',
            'users_expires_unit',
            'user_id_autoincrement',
            'user_id_autoincrement_prefix',
            'user_id_autoincrement_start',
            'users_portrait',
            'users_portrait_attr',
            'users_portrait_accept',
            'users_portrait_width',
            'users_portrait_height',
            'users_local_management_enabled',
            'users_exposed_attributes',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'groups_heading',
            'groups_form_attrmap',
            'groups_listing_columns',
            'groups_listing_default_column',
            'save'
        ])

    def test_general_settings_tiles(self):
        general_settings = root['settings']['ugm_general']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            general_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                general_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(general_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm/edit"'
        self.assertTrue(res.find(expected) > -1)

    def test_localmanager_settings_tiles(self):
        lm_settings = root['settings']['ugm_localmanager']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            lm_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                lm_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(lm_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/localmanager/edit"'
        self.assertTrue(res.find(expected) > -1)
