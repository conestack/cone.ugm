from cone.app import root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.model.user import User
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound


class TestBrowserUser(TileTestCase):
    layer = testing.ugm_layer

    def test_content_tile(self):
        users = root['users']
        user = users['uid2']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/users/uid2/login"'
        res = render_tile(user, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    def test_leftcolumn_tile(self):
        users = root['users']
        user = users['uid2']
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

    def test_rightcolumn_tile(self):
        users = root['users']
        user = users['uid2']
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

    def test_columnlisting_tile(self):
        users = root['users']
        user = users['uid2']
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
            'ajax:target="http://example.com/groups/group2">'
        )
        self.assertTrue(res.find(expected) > -1)

    def test_allcolumnlisting_tile(self):
        users = root['users']
        user = users['uid2']
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
            'ajax:target="http://example.com/groups/group1">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.remove_principals(users=['uid99'])
    def test_add_user(self):
        users = root['users']
        request = self.layer.new_request()
        request.params['factory'] = 'user'

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
        request.params['userform.cn'] = 'cn99'
        request.params['userform.sn'] = 'sn99'
        request.params['userform.mail'] = 'uid99@example.com'
        request.params['userform.password'] = 'secret99'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'add')
        expected = '<div class="text-danger">No user_id defined</div>'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.id'] = 'uid99'

        with self.layer.authenticated('manager'):
            res = render_tile(users, request, 'add')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertEqual(sorted(users.keys()), [
            'admin', 'editor', 'localmanager_1', 'localmanager_2', 'manager',
            'max', 'sepp', 'uid0', 'uid1', 'uid2', 'uid3', 'uid4', 'uid5',
            'uid6', 'uid7', 'uid8', 'uid9', 'uid99', 'viewer'
        ])

        user = users['uid99']
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.attrs['cn'], 'cn99')
        self.assertEqual(user.attrs['mail'], 'uid99@example.com')
        self.assertEqual(user.attrs['rdn'], 'uid99')
        self.assertEqual(user.attrs['login'], 'uid99')
        self.assertEqual(user.attrs['sn'], 'sn99')
        self.assertTrue(user.attrs['password'].startswith('{SSHA}'))

    @testing.temp_principals(users={'uid99': {'sn': 'Uid99', 'cn': 'Uid99'}})
    def test_edit_user(self, users, groups):
        user = users['uid99']
        request = self.layer.new_request()

        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'edit')
        expected = '<form action="http://example.com/users/uid99/edit"'
        self.assertTrue(res.find(expected) > -1)

        request.params['userform.cn'] = 'cn99'
        request.params['userform.sn'] = 'sn changed'
        request.params['userform.mail'] = 'changed@example.com'
        request.params['userform.password'] = '_NOCHANGE_'
        request.params['userform.principal_roles'] = []
        request.params['action.userform.save'] = '1'
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'edit')
        self.assertEqual(res, '')
        self.assertEqual(sorted(user.attrs.items()), [
            ('cn', 'cn99'),
            ('mail', 'changed@example.com'),
            ('rdn', 'uid99'),
            ('sn', 'sn changed')
        ])
