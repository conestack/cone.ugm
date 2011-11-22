cone.ugm.model.group
====================

::

    >>> layer.login('manager')

    >>> from cone.ugm.model.group import Group
    >>> from cone.app import root 
    >>> groups = root['groups']
    >>> group = groups['group0']
    >>> group
    <Group object 'group0' at ...>
    
    >>> isinstance(group, Group)
    True

Check Properties::

    >>> props = group.properties

Group object is editable::

    >>> props.editable
    True

Check Metadata::

    >>> md = group.metadata
    >>> md.title
    'Group'
    
    >>> md.description
    'Group'

The real group objects are available via .model::

    >>> group.model
    <Group object 'group0' at ...>
    
    >>> group.model.__class__
    <class 'node.ext.ldap.ugm._api.Group'>

XXX: model is too generic, needs discussion. If so generic I'd say .context,
otherwise more specific.

XXX: should all this below work on the application model user or on the data
model behind?

The attributes of the group are wrapped::

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
    
    >>> layer.logout()
