from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.user import AllGroupsColumnListing
from cone.ugm.browser.user import GroupsOfUserColumnListing
from cone.ugm.events import UserCreatedEvent
from cone.ugm.events import UserModifiedEvent
from cone.ugm.model.user import User
from cone.ugm.tests.fixtures import local_management_enabled
from cone.ugm.tests.fixtures import local_manager_principals
from cone.ugm.utils import general_settings
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound
from zope.event import classhandler


class BrowserUserTests:
    @testing.principals(users={'user_1': {}})
    def test_content_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/users/user_1/login"'
        res = render_tile(user, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_leftcolumn_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, user, request, 'leftcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'leftcolumn')
        expected = '<div class="card column left_column bg-primary-100">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_rightcolumn_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, user, request, 'rightcolumn')

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'rightcolumn')
        expected = '<div class="card column right_column">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        groups={'group_1': {}},
        membership={'group_1': ['user_1']},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, user, request, 'columnlisting')

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'columnlisting')
        expected = (
            '<li class="list-group-item d-flex justify-content-between "\n              '
            'ajax:target="http://example.com/groups/group_1">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        groups={'group_1': {}, 'group_2': {}},
        membership={'group_1': ['user_1']},
        roles={'manager': ['manager']},
    )
    def test_allcolumnlisting_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(HTTPForbidden, render_tile, user, request, 'allcolumnlisting')

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'allcolumnlisting')
        expected = (
            '<li class="list-group-item d-flex justify-content-between "\n              '
            'ajax:target="http://example.com/groups/group_1">'
        )
        self.assertTrue(res.find(expected) > -1)

        expected = (
            '<li class="list-group-item d-flex justify-content-between "\n              '
            'ajax:target="http://example.com/groups/group_2">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    def test_add_user(self):
        root = get_root()
        users = root['users']
        request = self.layer.new_request()
        request.params['factory'] = 'user'

        events_called = []

        @classhandler.handler(UserCreatedEvent)
        def on_user_created(event):
            events_called.append('UserCreatedEvent')

        with self.layer.authenticated('viewer'):
            self.expectError(HTTPForbidden, render_tile, users, request, 'add')

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'add')
        expected = '<form action="http://example.com/users/add"'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.id'] = ''
        request.params['userform.password'] = 'secret_1'
        request.params['userform.fullname'] = 'Max Mustermann'
        request.params['userform.email'] = 'max.mustermann@example.com'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'add')
        expected = 'has-error'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.id'] = 'user_1'

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'add')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertEqual(sorted(users.keys()), ['manager', 'user_1'])

        user = users['user_1']
        self.assertTrue(isinstance(user, User))
        self.assertTrue(bool(user.attrs['password']))
        self.assertEqual(user.attrs['fullname'], 'Max Mustermann')
        self.assertEqual(user.attrs['email'], 'max.mustermann@example.com')
        self.assertTrue('UserCreatedEvent' in events_called)

    @testing.principals(
        users={
            'manager': {},
            'user_1': {
                'fullname': 'Max Mustermann',
                'email': 'max.mustermann@example.com',
            },
        },
        roles={'manager': ['manager']},
    )
    def test_edit_user(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        self.assertEqual(user.attrs['fullname'], 'Max Mustermann')
        self.assertEqual(user.attrs['email'], 'max.mustermann@example.com')

        request = self.layer.new_request()

        events_called = []

        @classhandler.handler(UserModifiedEvent)
        def on_user_modified(event):
            events_called.append('UserModifiedEvent')

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        expected = '<form action="http://example.com/users/user_1/edit"'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.fullname'] = 'Susi Musterfrau'
        request.params['userform.email'] = 'susi.musterfrau@example.com'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertEqual(res, '')

        self.assertEqual(user.attrs['fullname'], 'Susi Musterfrau')
        self.assertEqual(user.attrs['email'], 'susi.musterfrau@example.com')
        self.assertTrue('UserModifiedEvent' in events_called)

    @testing.principals(
        users={'manager': {}, 'user_1': {}},
        groups={
            'group_1': {'groupname': 'Group 1'},
            'group_2': {'groupname': 'Group 2'},
        },
        membership={'group_1': ['user_1'], 'group_2': ['user_1']},
        roles={'manager': ['manager']},
    )
    def test_columnlisting_filter(self):
        user = get_root()['users']['user_1']
        listing = GroupsOfUserColumnListing()
        listing.model = user
        listing.request = self.layer.new_request()
        listing.request.params['filter'] = 'group_1'
        with self.layer.authenticated('manager'):
            listed = [item['sort_by'] for item in listing.listing_items]
        self.assertEqual(listed, ['group_1'])

    @local_manager_principals
    @local_management_enabled
    def test_allcolumnlisting_local_manager(self):
        user = get_root()['users']['managed_user']
        listing = AllGroupsColumnListing()
        listing.model = user
        listing.request = self.layer.new_request()
        with self.layer.authenticated('local_manager'):
            listed = sorted(item['sort_by'] for item in listing.listing_items)
        self.assertEqual(listed, ['managed_group_0', 'managed_group_1'])

    def _add_user_request(self, **params):
        request = self.layer.new_request()
        request.params['factory'] = 'user'
        request.params['userform.id'] = 'user_1'
        request.params['userform.password'] = 'secret_1'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        request.params.update(params)
        return request

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    @testing.invalidate_settings
    def test_add_user_login_name(self):
        settings = general_settings(get_root())
        settings.attrs.users_login_name_attr = 'email'
        users = get_root()['users']
        request = self._add_user_request(
            **{'userform.login': 'max@example.com', 'userform.email': ''}
        )
        with self.layer.authenticated('manager'):
            render_tile(users, request, 'add')
        self.assertEqual(users['user_1'].attrs['email'], 'max@example.com')

    @local_manager_principals
    @local_management_enabled
    def test_add_user_local_manager(self):
        # Users added by a local manager become members of the default groups
        users = get_root()['users']
        request = self._add_user_request()
        with self.layer.authenticated('local_manager'):
            render_tile(users, request, 'add')
        self.assertEqual(users['user_1'].model.group_ids, ['managed_group_1'])

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    def test_add_user_ajax(self):
        users = get_root()['users']
        request = self._add_user_request(ajax='1')
        with self.layer.authenticated('manager'):
            render_tile(users, request, 'add')
        continuation = request.environ['cone.app.continuation']
        self.assertEqual(
            [(action.target, action.name) for action in continuation],
            [
                ('http://example.com/users?pid=user_1', 'leftcolumn'),
                ('http://example.com/users?pid=user_1', 'rightcolumn'),
            ],
        )

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    def test_add_user_cancel(self):
        users = get_root()['users']
        request = self._add_user_request()
        del request.params['action.userform.save']
        request.params['action.userform.cancel'] = '1'
        with self.layer.authenticated('manager'):
            render_tile(users, request, 'add')
        self.assertEqual(request.environ['redirect'].location, 'http://example.com/users')
        self.assertEqual(users.keys(), ['manager'])

    def _edit_user_request(self, **params):
        request = self.layer.new_request()
        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.fullname'] = 'Susi Musterfrau'
        request.params['userform.email'] = 'susi.musterfrau@example.com'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        request.params.update(params)
        return request

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    @testing.invalidate_settings
    def test_edit_user_password_in_form_attrmap(self):
        # The password is never written as plain attribute, even if configured
        # as form attribute
        settings = general_settings(get_root())
        settings.attrs.users_form_attrmap['password'] = 'Password'
        user = get_root()['users']['user_1']
        request = self._edit_user_request()
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertEqual(user.attrs['fullname'], 'Susi Musterfrau')
        self.assertTrue(user.model.authenticate('secret'))

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_edit_user_password(self):
        user = get_root()['users']['user_1']
        request = self._edit_user_request(**{'userform.password': 'secret_1'})
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertTrue(user.model.authenticate('secret_1'))
        self.assertFalse(user.model.authenticate('secret'))

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_edit_user_came_from(self):
        user = get_root()['users']['user_1']
        request = self._edit_user_request(came_from='http%3A%2F%2Fexample.com%2Fusers')
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        self.assertEqual(
            request.environ['redirect'].location,
            'http://example.com/users?pid=user_1',
        )


class TestBrowserUser(TileTestCase, BrowserUserTests):
    layer = testing.ugm_layer
