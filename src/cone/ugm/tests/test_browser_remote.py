from cone.app import root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.model.utils import ugm_roles
from cone.ugm.model.utils import ugm_server
from node.ext.ldap import LDAPNode
from node.ext.ldap import ONELEVEL
from node.ext.ldap.ugm import RolesConfig
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import render_view_to_response
import json


class remote_user_test(testing.remove_principals):

    def prepare_roles(self):
        props = ugm_server(root).ldap_props
        node = LDAPNode('dc=my-domain,dc=com', props)
        node['ou=roles'] = LDAPNode()
        node['ou=roles'].attrs['objectClass'] = ['organizationalUnit']
        node()

        rcfg = RolesConfig(
            baseDN='ou=roles,dc=my-domain,dc=com',
            attrmap={
                'id': 'cn',
                'rdn': 'cn',
            },
            scope=ONELEVEL,
            queryFilter='(objectClass=groupOfNames)',
            objectClasses=['groupOfNames'],
            defaults={},
        )
        roles = ugm_roles(root)
        roles._ldap_rcfg = rcfg

    def cleanup_roles(self):
        roles = ugm_roles(root)
        roles._ldap_rcfg = None

    def __call__(self, fn):
        w = super(remote_user_test, self).__call__(fn)

        def wrapper(inst):
            self.prepare_roles()
            w(inst)
            self.cleanup_roles()
        return wrapper


class TestBrowserRemote(TileTestCase):
    layer = testing.ugm_layer

    @remote_user_test(users=['uid99', 'uid100', 'uid101', 'uid102'])
    def test_add_user(self):
        users = root['users']
        request = self.layer.new_request(type='json')

        # Need add permission
        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                users,
                request,
                name='remote_add_user'
            )

        # No id given
        request.params['id'] = ''
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'No user ID given.',
            'success': False
        })

        # Existent id given
        request.params['id'] = 'uid9'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'User with given ID already exists.',
            'success': False
        })

        # Try to add user just by id. Fails since some attributes are mandatory
        request.params['id'] = 'uid99'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': (
                '{\'info\': u"object class \'inetOrgPerson\' requires attribute '
                '\'sn\'", \'desc\': u\'Object class violation\'}'
            ),
            'success': False
        })

        # Add minimal valid user
        request.params['id'] = 'uid99'
        request.params['attr.sn'] = 'User 99'
        request.params['attr.cn'] = 'User 99'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Created user with ID 'uid99'.",
            'success': True
        })

        # Check new user
        user = users['uid99']
        self.assertFalse(user.model.context.changed)

        # This user has nor roles and is not member of a group
        self.assertEqual(user.model.roles, [])
        self.assertEqual(user.model.groups, [])

        # There was no password given, thus we cannot authenticate with this
        # user yet
        self.assertFalse(user.model.authenticate('secret'))

        user.model.passwd(None, 'secret')
        self.assertTrue(user.model.authenticate('secret'))

        # Create another user with initial password
        request.params['id'] = 'uid100'
        request.params['password'] = 'secret'
        request.params['attr.sn'] = 'User 100'
        request.params['attr.cn'] = 'User 100'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Created user with ID 'uid100'.",
            'success': True
        })

        user = users['uid100']
        self.assertTrue(user.model.authenticate('secret'))

        # Create user with initial roles. Message tells us if some of this
        # roles are not available
        request.params['id'] = 'uid101'
        request.params['password'] = 'secret'
        request.params['roles'] = 'editor,viewer,inexistent'
        request.params['attr.sn'] = 'User 101'
        request.params['attr.cn'] = 'User 101'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Role 'inexistent' given but inexistent. Created user with ID 'uid101'.",
            'success': True
        })

        # Create user with intial group membership. Message tells us if some of
        # this groups are not available
        request.params['id'] = 'uid102'
        request.params['password'] = 'secret'
        request.params['roles'] = 'editor,viewer,inexistent'
        request.params['groups'] = 'group0,group1,group99'
        request.params['attr.sn'] = 'User 102'
        request.params['attr.cn'] = 'User 102'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_add_user')
        self.assertEqual(json.loads(res.text), {
            'message': (
                "Role 'inexistent' given but inexistent. Group 'group99' "
                "given but inexistent. Created user with ID 'uid102'."
            ),
            'success': True
        })

        # Check created user
        user = users['uid102']
        self.assertEqual(sorted(user.model.group_ids), ['group0', 'group1'])
        self.assertEqual(sorted(user.model.roles), ['editor', 'viewer'])
        self.assertTrue(user.model.authenticate('secret'))

    @testing.temp_principals(users={'uid99': {'cn': 'Uid99', 'sn': 'Uid99'}})
    def test_delete_user(self, users, groups):
        request = self.layer.new_request(type='json')

        with self.layer.authenticated('viewer'):
            self.expectError(
                HTTPForbidden,
                render_view_to_response,
                users,
                request,
                name='remote_delete_user'
            )

        # No id given
        request.params['id'] = ''
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'No user ID given.',
            'success': False
        })

        # Inexistent id given
        request.params['id'] = 'uid456'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': 'User with given ID not exists.',
            'success': False
        })

        # Valid deletions
        request.params['id'] = 'uid99'
        with self.layer.authenticated('manager'):
            res = render_view_to_response(users, request, name='remote_delete_user')
        self.assertEqual(json.loads(res.text), {
            'message': "Deleted user with ID 'uid99\'.",
            'success': True
        })
