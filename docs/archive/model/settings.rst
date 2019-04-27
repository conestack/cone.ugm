cone.ugm.model.settings
=======================

Test imports::

    >>> from cone.ugm.model.settings import GroupsSettings
    >>> from cone.ugm.model.settings import ServerSettings
    >>> from cone.ugm.model.settings import UsersSettings
    >>> from node.base import OrderedNode
    >>> from node.ext.ldap.properties import LDAPProps
    >>> import cone.app
    >>> import cone.ugm
    >>> import os
    >>> import pkg_resources

App path for testing::

    >>> path = pkg_resources.resource_filename('cone.ugm', '')
    >>> path = os.path.sep.join(path.split(os.path.sep)[:-3])
    >>> path
    '...cone.ugm'

Dummy settings container::

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
    u'ldap_props_node'

    >>> md.description
    u'ldap_props_node_description'

LDAP users config::

    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> ucfg.baseDN
    u'ou=users,ou=groupOfNames_10_10,dc=my-domain,dc=com'

    >>> ucfg.attrmap
    {'cn': 'cn', 
    'userPassword': 'userPassword', 
    u'jpegPhoto': u'jpegPhoto', 
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
    u'user_settings_node'

    >>> md.description
    u'user_settings_node_description'

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
    u'group_settings_node'

    >>> md.description
    u'group_settings_node_description'

LDAP connectivity tests::

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

    >>> from cone.app.ugm import ugm_backend
    >>> backend = ugm_backend.ugm

    >>> backend
    <Ugm object 'ldap_ugm' at ...>

    >>> backend is ugm_backend.ugm
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
    >>> backend is ugm_backend.ugm
    False

    >>> props is settings['ugm_server'].ldap_props
    False

    >>> ucfg is settings['ugm_users'].ldap_ucfg
    False

    >>> gcfg is settings['ugm_groups'].ldap_gcfg
    False

Cleanup. Reset backend and prepare settings for following tests::

    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
