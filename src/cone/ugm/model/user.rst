cone.ugm.model.user
===================

Test imports::

    >>> from cone.app import root
    >>> from cone.ugm.model.user import User

User node::

    >>> layer.login('manager')

    >>> users = root['users']
    >>> user = users['uid0']
    >>> user
    <User object 'uid0' at ...>

    >>> isinstance(user, User)
    True

Properties::

    >>> user.properties
    <cone.app.model.Properties object at ...>

Metadata::

    >>> md = user.metadata
    >>> md.title
    u'user_node'

    >>> md.description
    u'user_node_description'

Backend user node is available at ``model``::

    >>> user.model
    <User object 'uid0' at ...>

    >>> user.model.__class__
    <class 'node.ext.ldap.ugm._api.User'>

XXX: model is too generic, should become ``context``

XXX: should all this below work on the application model user or on the data
model behind?

Attributes of the user are wrapped::

    >>> sorted(user.attrs.items())
    [('cn', u'cn0'), 
    ('mail', u'uid0@groupOfNames_10_10.com'), 
    ('rdn', u'uid0'), 
    ('sn', u'sn0')]

    >>> user.attrs['mail'] = 'foo'

# XXX: changed should be available on the user object::

    >>> user.attrs.changed
    True

    >>> user()
    >>> user.attrs.changed
    False

    >>> user.attrs['mail']
    u'foo'

    >>> del user.attrs['mail']
    >>> user.attrs['mail'] = 'uid0@users300.my-domain.com'
    >>> user()

ACL::

    >>> user.__acl__
    [('Allow', 'system.Authenticated', ['view_portrait']), 
    ('Allow', 'role:editor', ['view', 'manage_membership']), 
    ('Allow', 'role:admin', ['view', 'manage_membership', 'view_portrait', 
    'add', 'edit', 'delete', 'add_user', 'edit_user', 'delete_user', 
    'manage_expiration', 'add_group', 'edit_group', 'delete_group']), 
    ('Allow', 'role:manager', ['view', 'manage_membership', 'view_portrait', 
    'add', 'edit', 'delete', 'add_user', 'edit_user', 'delete_user', 
    'manage_expiration', 'add_group', 'edit_group', 'delete_group', 'manage']), 
    ('Allow', 'system.Everyone', ['login']), 
    ('Deny', 'system.Everyone', <pyramid.security.AllPermissionsList object at ...>)]

    >>> layer.logout()
