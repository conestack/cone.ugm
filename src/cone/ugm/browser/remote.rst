cone.ugm.browser.remote
=======================

Remote calls for 3rd party integration. Test bootstrapping::

    >>> from pyramid.view import render_view_to_response
    >>> from cone.app import root
    >>> from cone.ugm.model.utils import ugm_server, ugm_roles
    >>> from node.ext.ldap import LDAPNode, ONELEVEL
    >>> from node.ext.ldap.ugm import RolesConfig
    
    >>> props = ugm_server(root).ldap_props
    >>> node = LDAPNode('dc=my-domain,dc=com', props)
    >>> node['ou=roles'] = LDAPNode()
    >>> node['ou=roles'].attrs['objectClass'] = ['organizationalUnit']
    >>> node()
    
    >>> rcfg = RolesConfig(
    ...     baseDN='ou=roles,dc=my-domain,dc=com',
    ...     attrmap={
    ...         'id': 'cn',
    ...         'rdn': 'cn',
    ...     },
    ...     scope=ONELEVEL,
    ...     queryFilter='(objectClass=groupOfNames)',
    ...     objectClasses=['groupOfNames'],
    ...     defaults={},
    ... )
    >>> roles = ugm_roles(root)
    >>> roles._ldap_rcfg = rcfg
    
    >>> from cone.ugm import reset_auth_impl
    >>> reset_auth_impl()
    
    >>> users = root['users']

Add User
--------

Need add permission::

    >>> layer.login('viewer')    
    >>> request = layer.new_request(type='json')
    >>> request.params['id'] = ''

    >>> render_view_to_response(users, request, name='remote_add_user')
    Traceback (most recent call last):
      ...
    HTTPForbidden: 
    Unauthorized: <function remote_add_user at ...> 
    failed permission check

No id given::

    >>> layer.login('manager')
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "No user ID given.", "success": false}'
    
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', 
    u'uid6', u'uid7', u'uid8', u'uid9']

Existent id given::

    >>> request.params['id'] = 'uid9'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "User with given ID already exists.", "success": false}'

Try to add user just by id. Fails since some attributes are mandatory.::

    >>> request.params['id'] = 'uid99'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "{\'info\': \\"object class \'inetOrgPerson\' 
    requires attribute \'sn\'\\", \'desc\': \'Object class violation\'}", 
    "success": false}'

Add minimal valid user.::

    >>> request.params['id'] = 'uid99'
    >>> request.params['attr.sn'] = 'User 99'
    >>> request.params['attr.cn'] = 'User 99'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "Created user with ID \'uid99\'.", "success": true}'
    
    >>> user = users['uid99']

The user was physically created.::

    >>> user.model.context.changed
    False

This user has nor roles and is not member of a group.::

    >>> user.model.roles
    []
    
    >>> user.model.groups
    []

There was no password given, thus we cannot authenticate with this user yet.::

    >>> user.model.authenticate('secret')
    False
    
    >>> user.model.passwd(None, 'secret')
    >>> user.model.authenticate('secret')
    True
    
Create another user with initial password.::

    >>> request.params['id'] = 'uid100'
    >>> request.params['password'] = 'secret'
    >>> request.params['attr.sn'] = 'User 100'
    >>> request.params['attr.cn'] = 'User 100'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "Created user with ID \'uid100\'.", "success": true}'
    
    >>> user = users['uid100']
    >>> user.model.authenticate('secret')
    True

Create user with initial roles. Message tells us if some of this roles are not
available.::

    >>> request.params['id'] = 'uid101'
    >>> request.params['password'] = 'secret'
    >>> request.params['roles'] = 'editor,viewer,inexistent'
    >>> request.params['attr.sn'] = 'User 101'
    >>> request.params['attr.cn'] = 'User 101'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    
    >> res.body

    >>> layer.logout()