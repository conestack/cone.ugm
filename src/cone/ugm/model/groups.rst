cone.ugm.model.groups
=====================

Test imports::

    >>> from cone.app import root
    >>> from cone.ugm.model.groups import Groups

Groups container::

    >>> layer.login('manager')

    >>> groups = root['groups']
    >>> groups
    <Groups object 'groups' at ...>

    >>> isinstance(groups, Groups)
    True

Properties::

    >>> groups.properties
    <cone.app.model.Properties object at ...>

Metadata::

    >>> md = groups.metadata
    >>> md.title
    u'groups_node'

    >>> md.description
    u'groups_node_description'

Iter groups::

    >>> len([x for x in groups])
    12

Inexistent child::

    >>> groups['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: u'inexistent'

Children are group application nodes::

    >>> group = groups['group0']
    >>> group
    <Group object 'group0' at ...>

If group gets deleted, it's not deleted from the underlying backend, this is
needed for invalidation::

    >>> del groups['group0']
    >>> groups['group0']
    <Group object 'group0' at ...>

    >>> backend = groups.backend
    >>> backend
    <Groups object 'groups' at ...>

    >>> backend is groups.backend
    True

    >>> groups.invalidate()
    >>> backend is groups.backend
    False

ACL::

    >>> groups.__acl__
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
