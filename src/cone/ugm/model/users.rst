cone.ugm.model.users
====================

::

    >>> layer.login('manager')

    >>> from cone.ugm.model.users import Users
    >>> from cone.app import root 
    >>> users = root['users']
    >>> users
    <Users object 'users' at ...>

    >>> isinstance(users, Users)
    True

    >>> users.__class__
    <class 'cone.ugm.model.users.Users'>

Properties::

    >>> users.properties
    <cone.app.model.Properties object at ...>

Metadata::

    >>> md = users.metadata
    >>> md.title
    u'users_node'

    >>> md.description
    u'users_node_description'

Iter users::

    >>> from cone.ugm.model.utils import ugm_users
    >>> len([x for x in users])
    18

Inexistent child::

    >>> users['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: u'inexistent'

Children are user application nodes::

    >>> user = users['uid0']
    >>> user.__class__
    <class 'cone.ugm.model.user.User'>

If user gets deleted, it's not deleted from underlying backend, this behavior
is expected for app model invalidation::

    >>> del users['uid0']
    >>> users['uid0']
    <User object 'uid0' at ...>

    >>> backend = users.backend
    >>> backend.__class__
    <class 'node.ext.ldap.ugm._api.Users'>

    >>> backend is users.backend
    True

    >>> users.__class__
    <class 'cone.ugm.model.users.Users'>

    >>> users.invalidate()
    >>> backend is users.backend
    False

ACL::

    >>> users.__acl__
    [('Allow', 'role:editor', ['view', 'manage_membership']), 
    ('Allow', 'role:admin', ['view', 'manage_membership', 'view_portrait', 
    'add', 'edit', 'delete', 'add_user', 'edit_user', 'delete_user', 
    'manage_expiration', 'add_group', 'edit_group', 'delete_group']), 
    ('Allow', 'role:manager', ['view', 'manage_membership', 'view_portrait', 
    'add', 'edit', 'delete', 'add_user', 'edit_user', 'delete_user', 
    'manage_expiration', 'add_group', 'edit_group', 'delete_group', 'manage']), 
    ('Allow', 'system.Everyone', ['login']), 
    ('Deny', 'system.Everyone', <pyramid.security.AllPermissionsList object at ...>)]

    >>> layer.logout()
