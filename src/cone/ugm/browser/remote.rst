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
    
    >>> import cone.ugm
    >>> cone.ugm.backend = None
    >>> cone.ugm.model.utils.ugm_backend(root)
    <Ugm object 'ugm' at ...>
    
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
    >>> res.body
    '{"message": "Role \'inexistent\' given but inexistent. Created user 
    with ID \'uid101\'.", "success": true}'

Create user with intial group membership. Message tells us if some of this
groups are not available.::

    >>> user.parent.parent['groups'].keys()
    [u'group0', u'group1', u'group2', u'group3', u'group4', u'group5', 
    u'group6', u'group7', u'group8', u'group9']
    
    >>> request.params['id'] = 'uid102'
    >>> request.params['password'] = 'secret'
    >>> request.params['roles'] = 'editor,viewer,inexistent'
    >>> request.params['groups'] = 'group0,group1,group99'
    >>> request.params['attr.sn'] = 'User 102'
    >>> request.params['attr.cn'] = 'User 102'
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    >>> res.body
    '{"message": "Role \'inexistent\' given but inexistent. 
    Group \'group99\' given but inexistent. Created user with ID \'uid102\'.", 
    "success": true}'

Check created user.::

    >>> user = users['uid102']
    >>> user.model.groups
    [<Group object 'group0' at ...>, <Group object 'group1' at ...>]
    
    >>> user.model.roles
    [u'editor', u'viewer']
    
    >>> user.model.authenticate('secret')
    True
    
    >>> layer.logout()


Delete User
-----------

Need add permission::

    >>> layer.login('viewer')    
    >>> request = layer.new_request(type='json')
    >>> request.params['id'] = ''

    >>> render_view_to_response(users, request, name='remote_delete_user')
    Traceback (most recent call last):
      ...
    HTTPForbidden: 
    Unauthorized: <function remote_delete_user at ...> 
    failed permission check

No id given::

    >>> layer.login('manager')
    >>> res = render_view_to_response(users, request, name='remote_delete_user')
    >>> res.body
    '{"message": "No user ID given.", "success": false}'
    
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', 
    u'uid7', u'uid8', u'uid9', u'uid99', u'uid100', u'uid101', u'uid102']

Inexistent id given::

    >>> request.params['id'] = 'uid103'
    >>> res = render_view_to_response(users, request, name='remote_delete_user')
    >>> res.body
    '{"message": "User with given ID not exists.", "success": false}'

Valid deletions::

    >>> request.params['id'] = 'uid102'
    >>> res = render_view_to_response(users, request, name='remote_delete_user')
    >>> res.body
    '{"message": "Deleted user with ID \'uid102\'.", "success": true}'
    
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'uid99', u'uid100', u'uid101']

Cleanup::

    >>> del users['uid99']
    >>> del users['uid100']
    >>> del users['uid101']
    >>> users()
    >>> roles._ldap_rcfg = None
    >>> cone.ugm.model.utils.ugm_backend(root)
    <Ugm object 'ugm' at ...>

    >>> layer.logout()
