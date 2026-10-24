from cone.app import get_root
from cone.app.browser.layout import personal_tools
from cone.app.model import BaseNode
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.users import UsersColumnListing
from cone.ugm.browser.users import ViewUsersAction
from cone.ugm.model.users import Users
from cone.ugm.tests.fixtures import local_management_enabled
from cone.ugm.tests.fixtures import local_manager_principals
from pyramid.httpexceptions import HTTPForbidden
from unittest import mock


class BrowserUsersTests:
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
        roles={'manager': ['manager']},
    )
    def test_leftcolumn_tile(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, users, request, 'leftcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'leftcolumn')
        expected = '<div class="card column left_column">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={'manager': ['manager']},
    )
    def test_rightcolumn_tile(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, users, request, 'rightcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'rightcolumn')
        expected = '<div class="card column right_column bg-primary-100">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={'manager': ['manager']},
    )
    def test_columnlisting_tile(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, users, request, 'columnlisting')

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'columnlisting')
        expected = '<div class="columnlisting leftbatchsensitiv"'
        self.assertTrue(res.find(expected) > -1)

    def test_ViewUsersAction_without_users_container(self):
        action = ViewUsersAction()
        action.model = BaseNode()
        action.request = self.layer.new_request()
        self.assertFalse(action.display)

    def test_ViewUsersAction_without_view_permission(self):
        action = ViewUsersAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        self.assertFalse(action.display)

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    def test_ViewUsersAction(self):
        self.assertIsInstance(personal_tools['users'], ViewUsersAction)
        action = ViewUsersAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            self.assertTrue(action.display)
        self.assertEqual(action.target, 'http://example.com/users')
        self.assertEqual(action.href, 'http://example.com/users')

    @local_manager_principals
    @local_management_enabled
    def test_ViewUsersAction_local_manager(self):
        action = ViewUsersAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('local_manager'):
            self.assertTrue(action.display)

    @local_manager_principals
    @local_management_enabled
    def test_ViewUsersAction_without_local_manager_group(self):
        action = ViewUsersAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('editor'):
            self.assertFalse(action.display)

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        roles={'manager': ['manager']},
    )
    def test_rightcolumn_tile_principal_form(self):
        users = get_root()['users']
        request = self.layer.new_request()
        request.params['pid'] = 'user_1'
        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'rightcolumn')
        self.assertIn('<form action="http://example.com/users/user_1/edit"', res)
        # Opened in the right column, the form links to the user itself
        self.assertIn('ajax:target="http://example.com/users/user_1"', res)
        self.assertIn('<span class="bi-caret-right"></span>', res)

    def _listing(self):
        listing = UsersColumnListing()
        listing.model = get_root()['users']
        listing.request = self.layer.new_request()
        return listing

    def _listed_ids(self, listing):
        return sorted(item['sort_by'] for item in listing.listing_items)

    @testing.principals(
        users={'manager': {}, 'user_1': {}, 'user_2': {}},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_filter(self):
        listing = self._listing()
        listing.request.params['filter'] = 'user_1'
        with self.layer.authenticated('manager'):
            self.assertEqual(self._listed_ids(listing), ['user_1'])

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_current(self):
        listing = self._listing()
        listing.request.params['pid'] = 'user_1'
        with self.layer.authenticated('manager'):
            current = [
                item['sort_by'] for item in listing.listing_items if item['current']
            ]
        self.assertEqual(current, ['user_1'])

    def test_columnlisting_failing_backend(self):
        listing = self._listing()
        backend = mock.Mock()
        backend.search.side_effect = Exception('Backend not available')
        with mock.patch.object(Users, 'backend', backend):
            with self.assertLogs('cone.ugm', level='ERROR') as logs:
                self.assertEqual(listing.listing_items, [])
        self.assertIn('Failed to query listing items', logs.output[0])

    @local_manager_principals
    @local_management_enabled
    def test_columnlisting_local_manager(self):
        listing = self._listing()
        with self.layer.authenticated('local_manager'):
            self.assertEqual(self._listed_ids(listing), ['managed_user'])

    @local_manager_principals
    @local_management_enabled
    def test_columnlisting_without_local_manager_group(self):
        listing = self._listing()
        with self.layer.authenticated('editor'):
            self.assertEqual(listing.listing_items, [])


class TestBrowserUsers(TileTestCase, BrowserUsersTests):
    layer = testing.ugm_layer
