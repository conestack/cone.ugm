Local Manager
=============

Dummy environment::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> conf_path = os.path.join(tempdir, 'localmanager.xml')

Local manager configuration attributes::

    >>> from cone.ugm.model.localmanager import LocalManagerConfigAttributes
    >>> config = LocalManagerConfigAttributes(conf_path)
    >>> config
    <LocalManagerConfigAttributes object 'None' at ...>

Not exists yet::

    >>> os.path.exists(conf_path)
    False

After calling it does::

    >>> config()
    >>> os.path.exists(conf_path)
    True

    >>> with open(conf_path) as handle:
    ...     handle.read().split('\n')
    ['<localmanager/>', '']

Add rules::

    >>> config['foo'] = {
    ...     'target': ['bar', 'baz'],
    ...     'default': ['bar'],
    ... }

    >>> config['aaa'] = {
    ...     'target': ['bbb', 'ccc'],
    ...     'default': ['ccc'],
    ... }

Iter::

    >>> list(config)
    ['foo', 'aaa']

Modify a rule::

    >>> rule = config['foo']['default'] = ['bar']

Write config to file::

    >>> config()
    >>> with open(conf_path) as handle:
    ...     handle.read().split('\n')
    ['<localmanager>', 
    '  <foo>', 
    '    <target>', 
    '      <item>bar</item>', 
    '      <item>baz</item>', 
    '    </target>', 
    '    <default>', 
    '      <item>bar</item>', 
    '    </default>', 
    '  </foo>', 
    '  <aaa>', 
    '    <target>', 
    '      <item>bbb</item>', 
    '      <item>ccc</item>', 
    '    </target>', 
    '    <default>', 
    '      <item>ccc</item>', 
    '    </default>', 
    '  </aaa>', 
    '</localmanager>', 
    '']

Recreate on existing conf::

    >>> config = LocalManagerConfigAttributes(conf_path)
    >>> config.items()
    [('foo', {'default': ['bar'], 'target': ['bar', 'baz']}), 
    ('aaa', {'default': ['ccc'], 'target': ['bbb', 'ccc']})]

Cleanup dummy environment::

    >>> import shutil
    >>> shutil.rmtree(tempdir)

Local Manager test config::

    >>> from cone.app import get_root
    >>> root = get_root()

    >>> config = root['settings']['ugm_localmanager'].attrs
    >>> config.items()
    [('admin_group_1', 
    {'default': ['group1'], 'target': ['group0', 'group1']}), 
    ('admin_group_2', 
    {'default': ['group2'], 'target': ['group1', 'group2']})]

Local Manager plumbing behavior::

    >>> from plumber import plumber
    >>> from cone.app.model import BaseNode
    >>> from cone.ugm.model.localmanager import LocalManager
    >>> class LocalManagerNode(BaseNode):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = LocalManager

    >>> lm_node = LocalManagerNode(name='lm_node', parent=root)
    >>> lm_node.local_management_enabled
    False

``local_management_enabled`` is generally ignored in following
functions of ``LocalManager``. User needs to consider if local management is
enabled.

Unauthenticated::

    >>> lm_node.local_manager_target_gids
    []

    >>> lm_node.local_manager_target_uids
    []

Authenticated, no local manager::

    >>> layer.login('uid0')
    >>> lm_node.local_manager_target_gids
    []

    >>> lm_node.local_manager_target_uids
    []

    >>> layer.logout()

Authenticated, invalid local management group member::

    >>> groups = root['groups'].backend
    >>> group = groups['admin_group_2']
    >>> group.add('localmanager_1')
    >>> group()
    >>> group.member_ids
    [u'localmanager_2', u'localmanager_1']

    >>> layer.login('localmanager_1')
    >>> lm_node.local_manager_target_gids
    Traceback (most recent call last):
      ...
    Exception: Authenticated member defined in local manager groups 
    'admin_group_1', 'admin_group_2' but only one management group allowed 
    for each user. Please contact System Administrator in order to fix 
    this problem.

    >>> layer.logout()

    >>> del group['localmanager_1']
    >>> group()
    >>> group.member_ids
    [u'localmanager_2']

Authenticated, local manager::

    >>> layer.login('localmanager_1')
    >>> lm_node.local_manager_target_gids
    ['group0', 'group1']

    >>> lm_node.local_manager_target_uids
    [u'uid1']

    >>> layer.logout()
    >>> layer.login('localmanager_2')
    >>> lm_node.local_manager_target_gids
    ['group1', 'group2']

    >>> lm_node.local_manager_target_uids
    [u'uid2', u'uid1']

    >>> layer.logout()

Check of group id is marked as default::

    >>> lm_node.local_manager_is_default('admin_group_1', 'group0')
    False

    >>> lm_node.local_manager_is_default('admin_group_2', 'group0')
    Traceback (most recent call last):
      ...
    Exception: group 'group0' not managed by 'admin_group_2'

    >>> lm_node.local_manager_is_default('admin_group_1', 'group1')
    True

    >>> lm_node.local_manager_is_default('admin_group_2', 'group1')
    False

    >>> lm_node.local_manager_is_default('admin_group_1', 'group2')
    Traceback (most recent call last):
      ...
    Exception: group 'group2' not managed by 'admin_group_1'

    >>> lm_node.local_manager_is_default('admin_group_2', 'group2')
    True

Local manager ACL for users node::

    >>> users = root['users']
    >>> users.local_manager_acl
    []

    >>> layer.login('uid1')
    >>> users.local_manager_acl
    []

    >>> layer.logout()
    >>> layer.login('localmanager_1')
    >>> users.local_manager_acl
    [('Allow', u'localmanager_1', ['view', 'add', 'add_user', 'edit', 
    'edit_user', 'manage_expiration', 'manage_membership'])]

    >>> layer.logout()

Local manager ACL for groups node::

    >>> groups = root['groups']
    >>> groups.local_manager_acl
    []

    >>> layer.login('uid1')
    >>> groups.local_manager_acl
    []

    >>> layer.logout()
    >>> layer.login('localmanager_1')
    >>> groups.local_manager_acl
    [('Allow', u'localmanager_1', ['view', 'manage_membership'])]

    >>> layer.logout()

Local manager ACL for group node::

    >>> group0 = groups['group0']
    >>> group1 = groups['group1']
    >>> group2 = groups['group2']

    >>> group0.local_manager_acl
    []

    >>> group1.local_manager_acl
    []

    >>> group2.local_manager_acl
    []

    >>> layer.login('uid1')

    >>> group0.local_manager_acl
    []

    >>> group1.local_manager_acl
    []

    >>> group2.local_manager_acl
    []

    >>> layer.logout()

    >>> layer.login('localmanager_1')

    >>> group0.local_manager_acl
    [('Allow', u'localmanager_1', ['view', 'manage_membership'])]

    >>> group1.local_manager_acl
    [('Allow', u'localmanager_1', ['view', 'manage_membership'])]

    >>> group2.local_manager_acl
    []

    >>> layer.logout()

    >>> layer.login('localmanager_2')

    >>> group0.local_manager_acl
    []

    >>> group1.local_manager_acl
    [('Allow', u'localmanager_2', ['view', 'manage_membership'])]

    >>> group2.local_manager_acl
    [('Allow', u'localmanager_2', ['view', 'manage_membership'])]

    >>> layer.logout()

Local manager ACL for user node::

    >>> user1 = users['uid1']
    >>> user2 = users['uid2']

    >>> user1.local_manager_acl
    []

    >>> user2.local_manager_acl
    []

    >>> layer.login('uid1')

    >>> user1.local_manager_acl
    []

    >>> user2.local_manager_acl
    []

    >>> layer.logout()

    >>> layer.login('localmanager_1')

    >>> user1.local_manager_acl
    [('Allow', u'localmanager_1', 
    ['view', 'add', 'add_user', 'edit', 'edit_user', 
    'manage_expiration', 'manage_membership'])]

    >>> user2.local_manager_acl
    []

    >>> layer.logout()

    >>> layer.login('localmanager_2')

    >>> user1.local_manager_acl
    [('Allow', u'localmanager_2', 
    ['view', 'add', 'add_user', 'edit', 'edit_user', 
    'manage_expiration', 'manage_membership'])]

    >>> user2.local_manager_acl
    [('Allow', u'localmanager_2', 
    ['view', 'add', 'add_user', 'edit', 'edit_user', 
    'manage_expiration', 'manage_membership'])]

    >>> layer.logout()
