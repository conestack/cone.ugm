cone.ugm.model.group
====================

Test imports::

    >>> from cone.app import root
    >>> from cone.ugm.model.group import Group

Group node::

    >>> layer.login('manager')

    >>> groups = root['groups']
    >>> group = groups['group0']
    >>> group
    <Group object 'group0' at ...>

    >>> isinstance(group, Group)
    True

Properties::

    >>> group.properties
    <cone.app.model.Properties object at ...>

Metadata::

    >>> md = group.metadata
    >>> md.title
    u'group_node'

    >>> md.description
    u'group_node_description'

Backend group node is available at ``model``::

    >>> group.model
    <Group object 'group0' at ...>

    >>> group.model.__class__
    <class 'node.ext.ldap.ugm._api.Group'>

XXX: model is too generic, should become ``context``

XXX: should all this below work on the application model user or on the data
model behind?

Attributes of the group are wrapped::

    >>> group.attrs.items()
    [('member', [u'cn=nobody']), ('rdn', u'group0')]

    >>> group.attrs['businessCategory'] = 'Cat0'

# XXX: changed should be available on the group object::

    >>> group.attrs.changed
    True

    >>> group()
    >>> group.attrs.changed
    False

    >>> group.attrs['businessCategory']
    u'Cat0'

    >>> del group.attrs['businessCategory']
    >>> group()

ACL::

    >>> group.__acl__
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
