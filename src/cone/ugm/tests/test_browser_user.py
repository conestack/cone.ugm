from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.events import UserCreatedEvent
from cone.ugm.events import UserModifiedEvent
from cone.ugm.model.user import User
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound
from zope.event import classhandler


class TestBrowserUser(TileTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        users={
            'user_1': {}
        })
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
        users={
            'manager': {},
            'user_1': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_leftcolumn_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            user,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'leftcolumn')
        expected = '<div class="column left_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
            'user_1': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_rightcolumn_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            user,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'rightcolumn')
        expected = '<div class="column right_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
            'user_1': {}
        },
        groups={
            'group_1': {}
        },
        membership={
            'group_1': ['user_1']
        },
        roles={
            'manager': ['manager']
        })
    def test_columnlisting_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            user,
            request,
            'columnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'columnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/groups/group_1">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
            'user_1': {}
        },
        groups={
            'group_1': {},
            'group_2': {}

        },
        membership={
            'group_1': ['user_1']
        },
        roles={
            'manager': ['manager']
        })
    def test_allcolumnlisting_tile(self):
        root = get_root()
        users = root['users']
        user = users['user_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            user,
            request,
            'allcolumnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'allcolumnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/groups/group_1">'
        )
        self.assertTrue(res.find(expected) > -1)

        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/groups/group_2">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {}
        },
        roles={
            'manager': ['manager']
        })
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
            self.expectError(
                HTTPForbidden,
                render_tile,
                users,
                request,
                'add'
            )

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
        expected = '<div class="text-danger">No User ID defined</div>'
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
                'email': 'max.mustermann@example.com'
            }
        },
        roles={
            'manager': ['manager']
        })
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
            res = render_tile(user, request, 'edit')
        expected = '<form action="http://example.com/users/user_1/edit"'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.fullname'] = 'Susi Musterfrau'
        request.params['userform.email'] = 'susi.musterfrau@example.com'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'edit')
        self.assertEqual(res, '')

        self.assertEqual(user.attrs['fullname'], 'Susi Musterfrau')
        self.assertEqual(user.attrs['email'], 'susi.musterfrau@example.com')
        self.assertTrue('UserModifiedEvent' in events_called)
