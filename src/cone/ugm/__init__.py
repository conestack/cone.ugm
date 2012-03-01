import os
import logging
import cone.app
from pyramid.security import (
    Everyone,
    Allow,
    Deny,
    ALL_PERMISSIONS,
)
from cone.app.security import acl_registry
from cone.app.model import Properties
from cone.ugm.model.user import User
from cone.ugm.model.users import Users
from cone.ugm.model.group import Group
from cone.ugm.model.groups import Groups
from cone.ugm.model.settings import (
    GeneralSettings,
    ServerSettings,
    UsersSettings,
    GroupsSettings,
    RolesSettings,
)
from cone.ugm.model.users import users_factory
from cone.ugm.model.groups import groups_factory
from node.ext.ldap.ugm import Ugm


logger = logging.getLogger('cone.ugm')


# custom UGM styles
cone.app.cfg.css.protected.append('cone.ugm.static/styles.css')


# custom UGM javascript
cone.app.cfg.js.protected.append('cone.ugm.static/jQuery.sortElements.js')
cone.app.cfg.js.protected.append('cone.ugm.static/naturalSort.js')
cone.app.cfg.js.protected.append('cone.ugm.static/ugm.js')


# layout configuration
cone.app.cfg.layout.livesearch = False
cone.app.cfg.layout.pathbar = False
cone.app.cfg.layout.sidebar_left = []


# UGM settings
cone.app.register_plugin_config('ugm_general', GeneralSettings)
cone.app.register_plugin_config('ugm_server', ServerSettings)
cone.app.register_plugin_config('ugm_users', UsersSettings)
cone.app.register_plugin_config('ugm_groups', GroupsSettings)
cone.app.register_plugin_config('ugm_roles', RolesSettings)


# Users container
cone.app.register_plugin('users', users_factory)


# Groups container
cone.app.register_plugin('groups', groups_factory)


# security
admin_permissions = ['view', 'add', 'edit', 'delete', 'manage_membership']


ugm_default_acl = [
    (Allow, 'role:editor', ['view', 'manage_membership']),
    (Allow, 'role:admin', admin_permissions),
    (Allow, 'role:owner', admin_permissions),
    (Allow, 'role:manager', admin_permissions + ['manage']),
    (Allow, Everyone, ['login']),
    (Deny, Everyone, ALL_PERMISSIONS),
]


# register default acl's
acl_registry.register(ugm_default_acl, User, 'user')
acl_registry.register(ugm_default_acl, Users, 'users')
acl_registry.register(ugm_default_acl, Group, 'group')
acl_registry.register(ugm_default_acl, Groups, 'groups')


# application startup hooks
def initialize_ugm(config, global_config, local_config):
    """Initialize UGM.
    """
    # static resources
    config.add_view('cone.ugm.browser.static_resources', name='cone.ugm.static')


cone.app.register_main_hook(initialize_ugm)


def initialize_auth_impl(config, global_config, local_config):
    """Initialize LDAP based UGM implementation for cone.app as
    authentication implementation.
    
    XXX: move to cone.ldap later
    """
    os.environ['LDAP_CFG_FILE'] = local_config.get('cone.ugm.ldap_config', '')
    import cone.ugm
    ldap_auth = local_config.get('cone.auth_impl') == 'node.ext.ldap'
    if not ldap_auth:
        return
    reset_ldap_auth_impl()

cone.app.register_main_hook(initialize_auth_impl)


def reset_auth_impl():
    """LDAP only ATM.
    """
    return reset_ldap_auth_impl()


def reset_ldap_auth_impl():
    """XXX: Move to ``cone.ldap``.
    """
    import cone.app
    root = cone.app.get_root()
    settings = root['settings']
    server_settings = settings['ugm_server']
    if not server_settings.ldap_connectivity:
        logger.error(u"Could not initialize authentication implementation. "
                     u"LDAP Server is not available or invalid credentials.")
        return
    props = server_settings.ldap_props
    users_settings = settings['ugm_users']
    if not users_settings.ldap_users_container_valid:
        logger.error(u"Could not initialize authentication implementation. "
                     u"Configured users container invalid.")
        return
    ucfg = users_settings.ldap_ucfg
    groups_settings = settings['ugm_groups']
    gcfg = None
    if groups_settings.ldap_groups_container_valid:
        gcfg = groups_settings.ldap_gcfg
    else:
        logger.warning(u"Configured groups container invalid.")
    roles_settings = settings['ugm_roles']
    rcfg = None
    if roles_settings.ldap_roles_container_valid:
        rcfg = roles_settings.ldap_rcfg
    else:
        logger.warning(u"Configured roles container invalid.")
    ugm = Ugm(name='ldap_ugm', props=props, ucfg=ucfg, gcfg=gcfg, rcfg=rcfg)
    cone.app.cfg.auth = ugm
    return ugm