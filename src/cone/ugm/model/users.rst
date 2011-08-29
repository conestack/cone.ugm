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

Check Properties::

    >>> props = users.properties

Users object is not editable::

    >>> props.editable
    False

Check Metadata::

    >>> md = users.metadata
    >>> md.title
    'Users'
    
    >>> md.description
    'Container for Users'

Check for test users::

    >>> from cone.ugm.model.utils import ugm_users
    >>> len([x for x in users])
    10

Access inexistent child::

    >>> users['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

The children are user application nodes::
    
    >>> user = users['uid0']
    >>> user
    <User object 'uid0' at ...>

If we delete a user, it's not deleted from the underlying backend, this is
needed for invalidation::

    >>> del users['uid0']
    >>> users['uid0']
    <User object 'uid0' at ...>

Test invalidation::

    >>> backend = users.backend
    >>> backend
    <Users object 'users' at ...>
    
    >>> backend is users.backend
    True
    
    >>> users.invalidate()
    >>> backend is users.backend
    False

Check if ugm is not configured properly::

    >>> settings = root['settings']['ugm_server']
    >>> settings.invalidate()
    >>> [k for k in users]
    []

    >>> layer.logout()

Reset settings for following tests::

    >>> settings = root['settings']
    >>> settings['ugm_server'].invalidate()
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']

