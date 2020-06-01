from cone.app import get_root
from cone.app.model import XMLProperties
from cone.ugm import testing
from cone.ugm.settings import GeneralSettings
from cone.ugm.settings import UGMSettings
from node.tests import NodeTestCase
import os


class TestModelSettings(NodeTestCase):
    layer = testing.ugm_layer

    @testing.temp_directory
    def test_UGMSettings(self, tempdir):
        path = os.path.join(tempdir, 'settings.xml')

        class MyUGMSettings(UGMSettings):
            config_file = path
            initialize_ugm_on_invalidate = False

        settings = MyUGMSettings()
        expected = 'Configuration file {} not exists.'.format(path)
        err = self.expect_error(ValueError, lambda: settings.attrs)
        self.assertEqual(str(err), expected)

        with open(path, 'w') as f:
            f.write('<properties />')

        attrs = settings.attrs
        self.assertTrue(isinstance(attrs, XMLProperties))

        attrs.foo = 'foo'
        settings()

        with open(path, 'r') as f:
            content = f.read()
        expected = '<properties>\n  <foo>foo</foo>\n</properties>\n'
        self.assertEqual(content, expected)

        self.assertTrue(attrs is settings.attrs)
        settings.invalidate()
        self.assertFalse(attrs is settings.attrs)

    @testing.invalidate_settings
    def test_UGMGeneralSettings(self):
        settings = get_root()['settings']['ugm_general']

        self.assertTrue(isinstance(settings, GeneralSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'ugm_settings_node')
        self.assertEqual(md.description, 'ugm_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
            'groups_form_attrmap',
            'groups_listing_columns',
            'groups_listing_default_column',
            'roles_principal_roles_enabled',
            'user_id_autoincrement',
            'user_id_autoincrement_prefix',
            'user_id_autoincrement_start',
            'users_account_expiration',
            'users_expires_attr',
            'users_expires_unit',
            'users_exposed_attributes',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'users_local_management_enabled',
            'users_login_name_attr',
            'users_portrait',
            'users_portrait_accept',
            'users_portrait_attr',
            'users_portrait_height',
            'users_portrait_width',
        ])

        self.assertTrue(attrs is settings.attrs)
        settings.invalidate()
        self.assertFalse(attrs is settings.attrs)
