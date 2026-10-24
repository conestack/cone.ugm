from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.user import UserEditForm
from cone.ugm.model.user import User
from cone.ugm.utils import general_settings
from datetime import datetime
from unittest import mock


def account_expiration_enabled(fn):
    """Decorator for tests running with account expiration enabled."""

    def wrapper(*a, **kw):
        settings = general_settings(get_root())
        settings.attrs.users_account_expiration = 'True'
        try:
            fn(*a, **kw)
        finally:
            settings.invalidate()

    return wrapper


class BrowserExpiresTests:
    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_expiration_widget_disabled(self):
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertNotIn('userform.active', res)

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    @account_expiration_enabled
    def test_expiration_widget(self):
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertIn('name="userform.active"', res)

    @testing.principals(users={'user_1': {}})
    @account_expiration_enabled
    def test_expiration_widget_without_manage_expiration(self):
        form = UserEditForm()
        form.model = get_root()['users']['user_1']
        form.request = self.layer.new_request()
        with self.layer.authenticated('user_1'):
            form.prepare()
        self.assertEqual(form.form['active'].mode, 'display')

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    @account_expiration_enabled
    def test_save_expiration(self):
        # Whether the backend stores the expiration date depends on its
        # configuration, the form hands it over to the user anyway
        user = get_root()['users']['user_1']
        request = self.layer.new_request()
        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.active'] = '01.01.2030'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        with mock.patch.object(
            User, 'expires', new_callable=mock.PropertyMock, return_value=None
        ) as expires:
            with self.layer.authenticated('manager'):
                render_tile(user, request, 'editform')
        self.assertIn(mock.call(datetime(2030, 1, 1)), expires.mock_calls)


class TestBrowserExpires(TileTestCase, BrowserExpiresTests):
    layer = testing.ugm_layer
