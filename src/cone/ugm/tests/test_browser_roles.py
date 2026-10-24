from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.utils import general_settings


class BrowserRolesTests:
    def _edit_user_request(self, roles):
        request = self.layer.new_request()
        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.principal_roles'] = roles
        request.params['action.userform.save'] = '1'
        return request

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        roles={'manager': ['manager'], 'user_1': ['editor']},
    )
    def test_roles_widget(self):
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertIn('name="userform.principal_roles"', res)

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        roles={'manager': ['manager'], 'user_1': ['editor']},
    )
    def test_save_roles(self):
        user = get_root()['users']['user_1']
        request = self._edit_user_request(['viewer'])
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertEqual(user.model.roles, ['viewer'])

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        roles={'manager': ['manager'], 'user_1': ['editor']},
    )
    @testing.invalidate_settings
    def test_roles_disabled(self):
        settings = general_settings(get_root())
        settings.attrs.roles_principal_roles_enabled = 'False'
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertNotIn('name="userform.principal_roles"', res)

        request = self._edit_user_request(['viewer'])
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertEqual(user.model.roles, ['editor'])

    @testing.principals(
        users={'admin': {}, 'user_1': {}},
        roles={'admin': ['admin'], 'user_1': ['editor']},
    )
    def test_roles_without_manage_permission(self):
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        with self.layer.authenticated('admin'):
            res = render_tile(user, request, 'editform')
        self.assertIn('<form action="http://example.com/users/user_1/edit"', res)
        self.assertNotIn('name="userform.principal_roles"', res)

        request = self._edit_user_request(['viewer'])
        with self.layer.authenticated('admin'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertEqual(user.model.roles, ['editor'])


class TestBrowserRoles(TileTestCase, BrowserRolesTests):
    layer = testing.ugm_layer
