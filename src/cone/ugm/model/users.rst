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

Check Metadata::

    >>> md = users.metadata
    >>> md.title
    'Users'
    
    >>> md.description
    'Container for Users'

Check for test users::

    >>> from cone.ugm.model.utils import ugm_users
    >>> len([x for x in users])
    16

Access inexistent child::

    >>> users['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: u'inexistent'

The children are user application nodes::
    
    >>> user = users['uid0']
    >>> user.__class__
    <class 'cone.ugm.model.user.User'>

If we delete a user, it's not deleted from the underlying backend, this behavior
is expected for app model invalidation::

    >>> del users['uid0']
    >>> users['uid0']
    <User object 'uid0' at ...>

Test invalidation::

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

Check if ugm is not configured properly::

    >>> layer.logout()
