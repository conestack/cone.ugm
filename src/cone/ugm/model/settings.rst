cone.ugm.model.settings
=======================

App path for testing::

    >>> import os
    >>> import pkg_resources
    >>> path = pkg_resources.resource_filename('cone.ugm', '')
    >>> path = os.path.sep.join(path.split(os.path.sep)[:-3])
    >>> path
    '...cone.ugm'

Create dummy settings container::

    >>> from node.base import OrderedNode
    >>> from cone.ugm.model.settings import (
    ...     ServerSettings,
    ...     UsersSettings,
    ...     GroupsSettings,
    ... )
    >>> settings = OrderedNode()
    >>> settings['ugm_server'] = ServerSettings()
    >>> settings['ugm_users'] = UsersSettings()
    >>> settings['ugm_groups'] = GroupsSettings()

LDAP props::

    >>> props = settings['ugm_server'].ldap_props
    >>> props.uri
    u'ldap://127.0.0.1:12345'
    
    >>> props.user
    u'cn=Manager,dc=my-domain,dc=com'
    
    >>> props.password
    u'secret'
    
    >>> md = settings['ugm_server'].metadata
    >>> md.title
    'LDAP Props'
    
    >>> md.description
    'LDAP properties'

LDAP users config::

    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> ucfg.baseDN
    u'ou=users,ou=groupOfNames_10_10,dc=my-domain,dc=com'
    
    >>> ucfg.attrmap
    {'cn': 'cn', 
    'userPassword': 'userPassword', 
    'sn': 'sn', 
    'mail': 'mail', 
    'login': 'uid', 
    'rdn': 'uid', 
    'id': 'uid'}
    
    >>> ucfg.scope
    1
    
    >>> ucfg.queryFilter
    u''
    
    >>> ucfg.objectClasses
    [u'top', u'person', u'organizationalPerson', u'inetOrgPerson']
    
    >>> md = settings['ugm_users'].metadata
    >>> md.title
    'Users Settings'
    
    >>> md.description
    'LDAP users settings'

LDAP groups config::

    >>> gcfg = settings['ugm_groups'].ldap_gcfg
    >>> gcfg.baseDN
    u'ou=groups,ou=groupOfNames_10_10,dc=my-domain,dc=com'
    
    >>> gcfg.attrmap
    {'rdn': 'cn', 
    'id': 'cn'}
    
    >>> gcfg.scope
    1
    
    >>> gcfg.queryFilter
    u''
    
    >>> gcfg.objectClasses
    [u'groupOfNames']
    
    >>> md = settings['ugm_groups'].metadata
    >>> md.title
    'Groups Settings'
    
    >>> md.description
    'LDAP groups settings'

LDAP connectivity tests::

    >>> from node.ext.ldap.properties import LDAPProps
    >>> props = LDAPProps(
    ...     uri='ldap://127.0.0.1:12346/',
    ...     user='',
    ...     password='',
    ...     cache=False,
    ... )
    
    >>> settings['ugm_server']._ldap_props = props
    
    >>> settings['ugm_server'].ldap_connectivity
    False
    
    >>> settings['ugm_users'].ldap_users_container_valid
    False
    
    >>> settings['ugm_groups'].ldap_groups_container_valid
    False
    
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
    
    >>> settings['ugm_server'].ldap_connectivity
    True
    
    >>> settings['ugm_users'].ldap_users_container_valid
    True
    
    >>> settings['ugm_groups'].ldap_groups_container_valid
    True

Settings are written on ``__call__``. At the moment all settings are in one
file, so calling either ucfg, gcfg or props writes all of them::

    >>> settings['ugm_server']()

Test invalidate::

    >>> import cone.app
    >>> import cone.ugm
    
    >>> root = cone.app.root
    
    >>> settings = root['settings']
    >>> settings
    <AppSettings object 'settings' at ...>
    
    >>> props = settings['ugm_server'].ldap_props
    >>> props
    <node.ext.ldap.properties.LDAPServerProperties object at ...>
    
    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> ucfg
    <node.ext.ldap.ugm._api.UsersConfig object at ...>
    
    >>> gcfg = settings['ugm_groups'].ldap_gcfg
    >>> gcfg
    <node.ext.ldap.ugm._api.GroupsConfig object at ...>
    
    >>> from cone.ugm.model.utils import ugm_backend
    >>> backend = ugm_backend(root)
    
    >>> backend
    <Ugm object 'ldap_ugm' at ...>
    
    >>> backend is ugm_backend(root)
    True
    
    >>> settings = root['settings']
    >>> props = settings['ugm_server'].ldap_props
    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> gcfg = settings['ugm_groups'].ldap_gcfg
    
    >>> props is settings['ugm_server'].ldap_props
    True
    
    >>> ucfg is settings['ugm_users'].ldap_ucfg
    True
    
    >>> gcfg is settings['ugm_groups'].ldap_gcfg
    True
    
    >>> settings['ugm_server'].invalidate()
    >>> backend is ugm_backend(root)
    False
    
    >>> props is settings['ugm_server'].ldap_props
    False
    
    >>> ucfg is settings['ugm_users'].ldap_ucfg
    False
    
    >>> gcfg is settings['ugm_groups'].ldap_gcfg
    False

Reset backend and prepare settings for following tests::

    >>> cone.ugm.backend = None
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
