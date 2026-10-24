from cone.app import get_root
from cone.app.browser.layout import personal_tools
from cone.app.model import BaseNode
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.groups import GroupsColumnListing
from cone.ugm.browser.groups import ViewGroupsAction
from cone.ugm.model.groups import Groups
from cone.ugm.tests.fixtures import local_management_enabled
from cone.ugm.tests.fixtures import local_manager_principals
from pyramid.httpexceptions import HTTPForbidden
from unittest import mock


class BrowserGroupsTests:
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
        roles={'manager': ['manager']},
    )
    def test_leftcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, groups, request, 'leftcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'leftcolumn')
        expected = '<div class="card column left_column">'
        self.assertTrue(res.find(expected) > -1)
        # The add button small, so the header is as high as the one of the
        # right column - the height of every section card header
        self.assertIn('<button class="btn btn-sm btn-primary text-light"', res)

    @testing.principals(
        users={
            'manager': {},
        },
        roles={'manager': ['manager']},
    )
    def test_rightcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, groups, request, 'rightcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'rightcolumn')
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
        groups = root['groups']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, groups, request, 'columnlisting')

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'columnlisting')
        expected = '<div class="columnlisting leftbatchsensitiv"'
        self.assertTrue(res.find(expected) > -1)

    def test_ViewGroupsAction_without_groups_container(self):
        action = ViewGroupsAction()
        action.model = BaseNode()
        action.request = self.layer.new_request()
        self.assertFalse(action.display)

    def test_ViewGroupsAction_without_view_permission(self):
        action = ViewGroupsAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        self.assertFalse(action.display)

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    def test_ViewGroupsAction(self):
        self.assertIsInstance(personal_tools['groups'], ViewGroupsAction)
        action = ViewGroupsAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            self.assertTrue(action.display)
        self.assertEqual(action.target, 'http://example.com/groups')
        self.assertEqual(action.href, 'http://example.com/groups')

    @local_manager_principals
    @local_management_enabled
    def test_ViewGroupsAction_local_manager(self):
        action = ViewGroupsAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('local_manager'):
            self.assertTrue(action.display)

    @local_manager_principals
    @local_management_enabled
    def test_ViewGroupsAction_without_local_manager_group(self):
        action = ViewGroupsAction()
        action.model = get_root()
        action.request = self.layer.new_request()
        with self.layer.authenticated('editor'):
            self.assertFalse(action.display)

    @testing.principals(
        users={'manager': {}},
        groups={'group_1': {}},
        roles={'manager': ['manager']},
    )
    def test_rightcolumn_tile_principal_form(self):
        groups = get_root()['groups']
        request = self.layer.new_request()
        request.params['pid'] = 'group_1'
        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'rightcolumn')
        self.assertIn('<form action="http://example.com/groups/group_1/edit"', res)
        # Opened in the right column, the form links to the group itself
        self.assertIn('ajax:target="http://example.com/groups/group_1"', res)
        self.assertIn('<span class="bi-caret-right"></span>', res)

    def _listing(self):
        listing = GroupsColumnListing()
        listing.model = get_root()['groups']
        listing.request = self.layer.new_request()
        return listing

    def _listed_ids(self, listing):
        return sorted(item['sort_by'] for item in listing.listing_items)

    @testing.principals(
        users={'manager': {}},
        groups={'group_1': {}, 'group_2': {}},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_filter(self):
        listing = self._listing()
        listing.request.params['filter'] = 'group_1'
        with self.layer.authenticated('manager'):
            self.assertEqual(self._listed_ids(listing), ['group_1'])

    @testing.principals(
        users={'manager': {}},
        groups={'group_1': {}},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_current(self):
        listing = self._listing()
        listing.request.params['pid'] = 'group_1'
        with self.layer.authenticated('manager'):
            current = [
                item['sort_by'] for item in listing.listing_items if item['current']
            ]
        self.assertEqual(current, ['group_1'])

    def test_columnlisting_failing_backend(self):
        listing = self._listing()
        backend = mock.Mock()
        backend.search.side_effect = Exception('Backend not available')
        with mock.patch.object(Groups, 'backend', backend):
            with self.assertLogs('cone.ugm', level='ERROR') as logs:
                self.assertEqual(listing.listing_items, [])
        self.assertIn('Failed to query listing items', logs.output[0])

    @local_manager_principals
    @local_management_enabled
    def test_columnlisting_local_manager(self):
        listing = self._listing()
        with self.layer.authenticated('local_manager'):
            self.assertEqual(
                self._listed_ids(listing), ['managed_group_0', 'managed_group_1']
            )

    @local_manager_principals
    @local_management_enabled
    def test_columnlisting_without_local_manager_group(self):
        listing = self._listing()
        with self.layer.authenticated('editor'):
            self.assertEqual(listing.listing_items, [])


class TestBrowserGroups(TileTestCase, BrowserGroupsTests):
    layer = testing.ugm_layer
