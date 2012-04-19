cone.ugm.model.user
===================

::

    >>> layer.login('manager')

    >>> from cone.ugm.model.user import User
    >>> from cone.app import root 
    >>> users = root['users']
    >>> user = users['uid0']
    >>> user
    <User object 'uid0' at ...>
    
    >>> isinstance(user, User)
    True

Properties::

    >>> user.properties
    <cone.app.model.Properties object at ...>

Check Metadata::

    >>> md = user.metadata
    >>> md.title
    'User'
    
    >>> md.description
    'User'

The real user objects are available via .model::

    >>> user.model
    <User object 'uid0' at ...>
    
    >>> user.model.__class__
    <class 'node.ext.ldap.ugm._api.User'>

XXX: model is too generic, needs discussion. If so generic I'd say .context,
otherwise more specific.

XXX: should all this below work on the application model user or on the data
model behind?

The attributes of the user are wrapped::

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
    
    >>> layer.logout()
