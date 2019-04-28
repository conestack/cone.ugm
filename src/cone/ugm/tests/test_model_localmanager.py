from cone.app import get_root
from cone.app.model import BaseNode
from cone.ugm.model.localmanager import LocalManager
from cone.ugm.model.localmanager import LocalManagerConfigAttributes
from plumber import plumbing
import os
import shutil
import tempfile
from cone.ugm import testing
from node.tests import NodeTestCase


class TestModelLocalmanager(NodeTestCase):
    layer = testing.ugm_layer

    def test_LocalManagerConfigAttributes(self):
        # Dummy environment
        tempdir = tempfile.mkdtemp()
        conf_path = os.path.join(tempdir, 'localmanager.xml')

        # Local manager configuration attributes
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

        # Cleanup dummy environment
        shutil.rmtree(tempdir)

    def test_LocalManager(self):
        self.layer.new_request()

        # Local Manager test config
        root = get_root()

        config = root['settings']['ugm_localmanager'].attrs
        self.assertEqual(sorted(config.items()), [
            ('admin_group_1', {'default': ['group1'], 'target': ['group0', 'group1']}),
            ('admin_group_2', {'default': ['group2'], 'target': ['group1', 'group2']})
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
        self.assertEqual(lm_node.local_manager_target_gids, [])
        self.assertEqual(lm_node.local_manager_target_uids, [])

        # Authenticated, no local manager
        with self.layer.authenticated('uid0'):
            self.assertEqual(lm_node.local_manager_target_gids, [])
            self.assertEqual(lm_node.local_manager_target_uids, [])

        # Authenticated, invalid local management group member
        groups = root['groups'].backend
        group = groups['admin_group_2']
        group.add('localmanager_1')
        group()
        self.assertEqual(sorted(group.member_ids), ['localmanager_1', 'localmanager_2'])

        with self.layer.authenticated('localmanager_1'):
            err = self.expect_error(
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

        del group['localmanager_1']
        group()
        self.assertEqual(group.member_ids, [u'localmanager_2'])

        # Authenticated, local manager
        with self.layer.authenticated('localmanager_1'):
            self.assertEqual(
                sorted(lm_node.local_manager_target_gids),
                ['group0', 'group1']
            )
            self.assertEqual(lm_node.local_manager_target_uids, ['uid1'])

        with self.layer.authenticated('localmanager_2'):
            self.assertEqual(
                sorted(lm_node.local_manager_target_gids),
                ['group1', 'group2']
            )
            self.assertEqual(
                sorted(lm_node.local_manager_target_uids),
                ['uid1', 'uid2']
            )

        # Check of group id is marked as default
        self.assertFalse(lm_node.local_manager_is_default('admin_group_1', 'group0'))
        err = self.expect_error(
            Exception,
            lm_node.local_manager_is_default,
            'admin_group_2',
            'group0'
        )
        expected = "group 'group0' not managed by 'admin_group_2'"
        self.assertEqual(str(err), expected)
        self.assertTrue(lm_node.local_manager_is_default('admin_group_1', 'group1'))
        self.assertFalse(lm_node.local_manager_is_default('admin_group_2', 'group1'))
        err = self.expect_error(
            Exception,
            lm_node.local_manager_is_default,
            'admin_group_1',
            'group2'
        )
        expected = "group 'group2' not managed by 'admin_group_1'"
        self.assertEqual(str(err), expected)
        self.assertTrue(lm_node.local_manager_is_default('admin_group_2', 'group2'))

    def test_LocalManagerACL(self):
        root = get_root()
        self.layer.new_request()

        # Local manager ACL for users node
        users = root['users']
        self.assertEqual(users.local_manager_acl, [])

        with self.layer.authenticated('uid1'):
            self.assertEqual(users.local_manager_acl, [])

        with self.layer.authenticated('localmanager_1'):
            self.assertEqual(users.local_manager_acl, [
                ('Allow', 'localmanager_1', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])

        # Local manager ACL for groups node
        groups = root['groups']
        self.assertEqual(groups.local_manager_acl, [])

        with self.layer.authenticated('uid1'):
            self.assertEqual(groups.local_manager_acl, [])

        with self.layer.authenticated('localmanager_1'):
            self.assertEqual(groups.local_manager_acl, [
                ('Allow', 'localmanager_1', ['view', 'manage_membership'])
            ])

        # Local manager ACL for group node
        group0 = groups['group0']
        group1 = groups['group1']
        group2 = groups['group2']

        self.assertEqual(group0.local_manager_acl, [])
        self.assertEqual(group1.local_manager_acl, [])
        self.assertEqual(group2.local_manager_acl, [])

        with self.layer.authenticated('uid1'):
            self.assertEqual(group0.local_manager_acl, [])
            self.assertEqual(group1.local_manager_acl, [])
            self.assertEqual(group2.local_manager_acl, [])

        with self.layer.authenticated('localmanager_1'):
            self.assertEqual(group0.local_manager_acl, [
                ('Allow', 'localmanager_1', ['view', 'manage_membership'])
            ])
            self.assertEqual(group1.local_manager_acl, [
                ('Allow', 'localmanager_1', ['view', 'manage_membership'])
            ])
            self.assertEqual(group2.local_manager_acl, [])

        with self.layer.authenticated('localmanager_2'):
            self.assertEqual(group0.local_manager_acl, [])
            self.assertEqual(group1.local_manager_acl, [
                ('Allow', 'localmanager_2', ['view', 'manage_membership'])
            ])
            self.assertEqual(group2.local_manager_acl, [
                ('Allow', 'localmanager_2', ['view', 'manage_membership'])
            ])

        # Local manager ACL for user node
        user1 = users['uid1']
        user2 = users['uid2']

        self.assertEqual(user1.local_manager_acl, [])
        self.assertEqual(user2.local_manager_acl, [])

        with self.layer.authenticated('uid1'):
            self.assertEqual(user1.local_manager_acl, [])
            self.assertEqual(user2.local_manager_acl, [])

        with self.layer.authenticated('localmanager_1'):
            self.assertEqual(user1.local_manager_acl, [
                ('Allow', 'localmanager_1', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
            self.assertEqual(user2.local_manager_acl, [])

        with self.layer.authenticated('localmanager_2'):
            self.assertEqual(user1.local_manager_acl, [
                ('Allow', 'localmanager_2', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
            self.assertEqual(user2.local_manager_acl, [
                ('Allow', 'localmanager_2', [
                    'view', 'add', 'add_user', 'edit', 'edit_user',
                    'manage_expiration', 'manage_membership'
                ])
            ])
