import logging
import cone.app
from cone.app.model import Properties
from cone.ugm.model.settings import (
    ServerSettings,
    UsersSettings,
    GroupsSettings,
    RolesSettings,
)
from cone.ugm.model.users import Users
from cone.ugm.model.groups import Groups
from node.ext.ldap.ugm import Ugm


logger = logging.getLogger('cone.ugm')


# custom UGM styles
cone.app.cfg.css.protected.append('cone.ugm.static/styles.css')


# custom UGM javascript
cone.app.cfg.js.protected.append('cone.ugm.static/ugm.js')


# layout configuration
cone.app.cfg.layout.livesearch = False
cone.app.cfg.layout.pathbar = False
cone.app.cfg.layout.sidebar_left = []


# UGM settings
cone.app.register_plugin_config('ugm_server', ServerSettings)
cone.app.register_plugin_config('ugm_users', UsersSettings)
cone.app.register_plugin_config('ugm_groups', GroupsSettings)
cone.app.register_plugin_config('ugm_roles', RolesSettings)

# Users container
cone.app.register_plugin('users', Users)


# Groups container
cone.app.register_plugin('groups', Groups)


# The node.ext.ugm implementation to use for user and group management
# currently only LDAP
# XXX: take from cone.app.cfg.auth
backend = None


# Flag whether LDAP ugm implementation should be used for authentication
# XXX: move to cone.ldap later
ldap_auth_enabled = False


def reset_auth_impl():
    import cone.ugm
    if not cone.ugm.ldap_auth_enabled:
        return
    auth = cone.app.cfg.auth
    to_del = list()
    for impl in auth:
        if isinstance(impl, Ugm):
            to_del.append(impl)
    for impl in to_del:
        auth.remove(impl)
    cone.app.cfg.auth.append(backend)


def initialize_auth_impl(config, global_config, local_config):
    """Initialize LDAP based UGM implementation for cone.app as
    authentication implementation.
    """
    import cone.ugm
    cone.ugm.ldap_auth_enabled = local_config.get('cone.ugm.ldap_auth')
    if not cone.ugm.ldap_auth_enabled:
        return
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
    auth = cone.app.cfg.auth
    to_del = list()
    for impl in auth:
        if isinstance(impl, Ugm):
            to_del.append(impl)
    for impl in to_del:
        auth.remove(impl)
    cone.app.cfg.auth.append(ugm)

cone.app.register_main_hook(initialize_auth_impl)