from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.events import GroupCreatedEvent
from cone.ugm.events import GroupModifiedEvent
from cone.ugm.model.group import Group
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound
from zope.event import classhandler


class TestBrowserGroup(TileTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        groups={
            'group_1': {}
        })
    def test_content_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']
        request = self.layer.new_request()

        # Unauthenticated content tile renders login form
        expected = '<form action="http://example.com/groups/group_1/login"'
        res = render_tile(group, request, 'content')
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {}
        },
        groups={
            'group_1': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_leftcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'leftcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'leftcolumn')
        expected = '<div class="column left_column col-md-6">'
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {}
        },
        groups={
            'group_1': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_rightcolumn_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'rightcolumn'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'rightcolumn')
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
        groups = root['groups']
        group = groups['group_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'columnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'columnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/user_1">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {},
            'user_1': {},
            'user_2': {}
        },
        groups={
            'group_1': {}
        },
        membership={
            'group_1': [
                'user_1'
            ]
        },
        roles={
            'manager': ['manager']
        })
    def test_allcolumnlisting_tile(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']
        request = self.layer.new_request()

        self.expectError(
            HTTPForbidden,
            render_tile,
            group,
            request,
            'allcolumnlisting'
        )

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'allcolumnlisting')
        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/user_1">'
        )
        self.assertTrue(res.find(expected) > -1)

        expected = (
            '<li class="list-group-item "\n              '
            'ajax:target="http://example.com/users/user_2">'
        )
        self.assertTrue(res.find(expected) > -1)

    @testing.principals(
        users={
            'manager': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_add_group(self):
        root = get_root()
        groups = root['groups']
        request = self.layer.new_request()
        request.params['factory'] = 'group'

        events_called = []

        @classhandler.handler(GroupCreatedEvent)
        def on_group_created(event):
            events_called.append('GroupCreatedEvent')

        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                groups,
                request,
                'add'
            )

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        expected = '<form action="http://example.com/groups/add"'
        self.assertTrue(res.find(expected) > -1)

        request.params['groupform.id'] = ''
        request.params['groupform.groupname'] = 'Group 1'
        request.params['groupform.principal_roles'] = []
        request.params['action.groupform.save'] = '1'

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        expected = '<div class="text-danger">No Group ID defined</div>'
        self.assertTrue(res.find(expected) > -1)

        request.params['groupform.id'] = 'group_1'

        with self.layer.authenticated('manager'):
            res = render_tile(groups, request, 'add')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertEqual(sorted(groups.keys()), ['group_1'])

        group = groups['group_1']
        self.assertTrue(isinstance(group, Group))
        self.assertEqual(group.attrs['groupname'], 'Group 1')
        self.assertTrue('GroupCreatedEvent' in events_called)

    @testing.principals(
        users={
            'manager': {}
        },
        groups={
            'group_1': {
                'groupname': 'Group 1'
            }
        },
        roles={
            'manager': ['manager']
        })
    def test_edit_group(self):
        root = get_root()
        groups = root['groups']
        group = groups['group_1']
        self.assertEqual(group.attrs['groupname'], 'Group 1')

        request = self.layer.new_request()

        events_called = []

        @classhandler.handler(GroupModifiedEvent)
        def on_user_created(event):
            events_called.append('GroupModifiedEvent')

        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'edit')
        expected = '<form action="http://example.com/groups/group_1/edit"'
        self.assertTrue(res.find(expected) > -1)

        request.params['groupform.groupname'] = 'Groupname Changed'
        request.params['groupform.principal_roles'] = []
        request.params['action.groupform.save'] = '1'
        with self.layer.authenticated('manager'):
            res = render_tile(group, request, 'edit')
        self.assertEqual(res, '')

        self.assertEqual(group.attrs['groupname'], 'Groupname Changed')
        self.assertTrue('GroupModifiedEvent' in events_called)
