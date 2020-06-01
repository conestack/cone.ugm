from cone.app import get_root
from cone.app.model import BaseNode
from cone.ugm import testing
from cone.ugm.localmanager import LocalManager
from cone.ugm.localmanager import LocalManagerConfigAttributes
from node.tests import NodeTestCase
from plumber import plumbing
import os


class TestModelLocalmanager(NodeTestCase):
    layer = testing.ugm_layer

    @testing.temp_directory
    def test_LocalManagerConfigAttributes(self, tempdir):
        # Local manager configuration attributes
        conf_path = os.path.join(tempdir, 'localmanager.xml')
        config = LocalManagerConfigAttributes(conf_path)

        # Not exists yet
        self.assertFalse(os.path.exists(conf_path))

        # After calling it does
        config()
        self.assertTrue(os.path.exists(conf_path))

        with open(conf_path) as handle:
            data = handle.read().split('\n')
        self.assertEqual(data, ['<localmanager/>', ''])

        # Add rules
        config['foo'] = {
            'target': ['bar', 'baz'],
            'default': ['bar'],
        }
        config['aaa'] = {
            'target': ['bbb', 'ccc'],
            'default': ['ccc'],
        }

        # Iter
        self.assertEqual(sorted(list(config)), ['aaa', 'foo'])

        # Modify a rule
        config['foo']['default'] = ['bar']

        # Write config to file
        config()

        # Recreate on existing conf
        config = LocalManagerConfigAttributes(conf_path)
        self.assertEqual(sorted(config.items()), [
            ('aaa', {'default': ['ccc'], 'target': ['bbb', 'ccc']}),
            ('foo', {'default': ['bar'], 'target': ['bar', 'baz']})
        ])

    @testing.principals(
        users={
            'local_manager_1': {},
            'local_manager_2': {},
            'managed_user_1': {},
            'managed_user_2': {}
        },
        groups={
            'admin_group_1': {},
            'admin_group_2': {},
            'managed_group_0': {},
            'managed_group_1': {},
            'managed_group_2': {}
        },
        membership={
            'admin_group_1': ['local_manager_1'],
            'admin_group_2': ['local_manager_2'],
            'managed_group_1': ['managed_user_1'],
            'managed_group_2': ['managed_user_1', 'managed_user_2'],
        })
    def test_LocalManager(self):
        root = get_root()
        config = root['settings']['ugm_localmanager'].attrs
        self.assertEqual(sorted(config.items()), [
            ('admin_group_1', {
                'default': ['managed_group_1'],
                'target': ['managed_group_0', 'managed_group_1']
            }),
            ('admin_group_2', {
                'default': ['managed_group_2'],
                'target': ['managed_group_1', 'managed_group_2']
            })
        ])

        # Local Manager plumbing behavior
        @plumbing(LocalManager)
        class LocalManagerNode(BaseNode):
            pass

        lm_node = LocalManagerNode(name='lm_node', parent=root)
        self.assertFalse(lm_node.local_management_enabled)

        # ``local_management_enabled`` is generally ignored in following
        # functions of ``LocalManager``. User needs to consider if local
        # management is enabled.

        # Unauthenticated
        self.layer.new_request()
        self.assertEqual(lm_node.local_manager_target_gids, [])
        self.assertEqual(lm_node.local_manager_target_uids, [])

        # Authenticated, no local manager
        with self.layer.authenticated('inexistent'):
            self.assertEqual(lm_node.local_manager_target_gids, [])
            self.assertEqual(lm_node.local_manager_target_uids, [])

        # Authenticated, invalid local management group member
        groups = root['groups'].backend
        group = groups['admin_group_2']
        group.add('local_manager_1')
        group()
        self.assertEqual(sorted(group.member_ids), [
            'local_manager_1',
            'local_manager_2'
        ])

        with self.layer.authenticated('local_manager_1'):
            err = self.expectError(
                Exception,
                lambda: lm_node.local_manager_target_gids
            )
        expected = (
            "Authenticated member defined in local manager groups "
            "'admin_group_1', 'admin_group_2' but only one management group allowed "
            "for each user. Please contact System Administrator in order to fix "
            "this problem."
        )
        self.assertEqual(str(err), expected)

        del group['local_manager_1']
        group()
        self.assertEqual(group.member_ids, [u'local_manager_2'])

        # Authenticated, local manager
        with self.layer.authenticated('local_manager_1'):
            self.assertEqual(
                sorted(lm_node.local_manager_target_gids),
                ['managed_group_0', 'managed_group_1']
            )
            self.assertEqual(
                lm_node.local_manager_target_uids,
                ['managed_user_1']
            )

        with self.layer.authenticated('local_manager_2'):
            self.assertEqual(
                sorted(lm_node.local_manager_target_gids),
                ['managed_group_1', 'managed_group_2']
            )
            self.assertEqual(
                sorted(lm_node.local_manager_target_uids),
                ['managed_user_1', 'managed_user_2']
            )

        # Check if group id is marked as default
        self.assertFalse(lm_node.local_manager_is_default(
            'admin_group_1',
            'managed_group_0'
        ))
        err = self.expect_error(
            Exception,
            lm_node.local_manager_is_default,
            'admin_group_2',
            'managed_group_0'
        )
        expected = "group 'managed_group_0' not managed by 'admin_group_2'"
        self.assertEqual(str(err), expected)
        self.assertTrue(lm_node.local_manager_is_default(
            'admin_group_1',
            'managed_group_1'
        ))
        self.assertFalse(lm_node.local_manager_is_default(
            'admin_group_2',
            'managed_group_1'
        ))
        err = self.expect_error(
            Exception,
            lm_node.local_manager_is_default,
            'admin_group_1',
            'managed_group_2'
        )
        expected = "group 'managed_group_2' not managed by 'admin_group_1'"
        self.assertEqual(str(err), expected)
        self.assertTrue(lm_node.local_manager_is_default(
            'admin_group_2',
            'managed_group_2'
        ))

    @testing.principals(
        users={
            'local_manager_1': {},
            'local_manager_2': {},
            'managed_user_1': {},
            'managed_user_2': {}
        },
        groups={
            'admin_group_1': {},
            'admin_group_2': {},
            'managed_group_0': {},
            'managed_group_1': {},
            'managed_group_2': {}
        },
        membership={
            'admin_group_1': ['local_manager_1'],
            'admin_group_2': ['local_manager_2'],
            'managed_group_1': ['managed_user_1'],
            'managed_group_2': ['managed_user_1', 'managed_user_2'],
        })
    def test_LocalManagerACL(self):
        root = get_root()
        self.layer.new_request()

        # Local manager ACL for users node
        users = root['users']
        self.assertEqual(users.local_manager_acl, [])

        with self.layer.authenticated('managed_user_1'):
            self.assertEqual(users.local_manager_acl, [])

        with self.layer.authenticated('local_manager_1'):
            self.assertEqual(users.local_manager_acl, [
                ('Allow', 'local_manager_1', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])

        # Local manager ACL for groups node
        groups = root['groups']
        self.assertEqual(groups.local_manager_acl, [])

        with self.layer.authenticated('managed_user_1'):
            self.assertEqual(groups.local_manager_acl, [])

        with self.layer.authenticated('local_manager_1'):
            self.assertEqual(groups.local_manager_acl, [
                ('Allow', 'local_manager_1', ['view', 'manage_membership'])
            ])

        # Local manager ACL for group node
        managed_group_0 = groups['managed_group_0']
        managed_group_1 = groups['managed_group_1']
        managed_group_2 = groups['managed_group_2']

        self.assertEqual(managed_group_0.local_manager_acl, [])
        self.assertEqual(managed_group_1.local_manager_acl, [])
        self.assertEqual(managed_group_2.local_manager_acl, [])

        with self.layer.authenticated('managed_user_1'):
            self.assertEqual(managed_group_0.local_manager_acl, [])
            self.assertEqual(managed_group_1.local_manager_acl, [])
            self.assertEqual(managed_group_2.local_manager_acl, [])

        with self.layer.authenticated('local_manager_1'):
            self.assertEqual(managed_group_0.local_manager_acl, [
                ('Allow', 'local_manager_1', ['view', 'manage_membership'])
            ])
            self.assertEqual(managed_group_1.local_manager_acl, [
                ('Allow', 'local_manager_1', ['view', 'manage_membership'])
            ])
            self.assertEqual(managed_group_2.local_manager_acl, [])

        with self.layer.authenticated('local_manager_2'):
            self.assertEqual(managed_group_0.local_manager_acl, [])
            self.assertEqual(managed_group_1.local_manager_acl, [
                ('Allow', 'local_manager_2', ['view', 'manage_membership'])
            ])
            self.assertEqual(managed_group_2.local_manager_acl, [
                ('Allow', 'local_manager_2', ['view', 'manage_membership'])
            ])

        # Local manager ACL for user node
        managed_user_1 = users['managed_user_1']
        managed_user_2 = users['managed_user_2']

        self.assertEqual(managed_user_1.local_manager_acl, [])
        self.assertEqual(managed_user_2.local_manager_acl, [])

        with self.layer.authenticated('managed_user_1'):
            self.assertEqual(managed_user_1.local_manager_acl, [])
            self.assertEqual(managed_user_2.local_manager_acl, [])

        with self.layer.authenticated('local_manager_1'):
            self.assertEqual(managed_user_1.local_manager_acl, [
                ('Allow', 'local_manager_1', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
            self.assertEqual(managed_user_2.local_manager_acl, [])

        with self.layer.authenticated('local_manager_2'):
            self.assertEqual(managed_user_1.local_manager_acl, [
                ('Allow', 'local_manager_2', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
            self.assertEqual(managed_user_2.local_manager_acl, [
                ('Allow', 'local_manager_2', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
