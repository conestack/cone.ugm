import cone.app
from cone.app.model import Properties
from cone.ugm.model.settings import (
    ServerSettings,
    UsersSettings,
    GroupsSettings,
)
from cone.ugm.model.users import Users
from cone.ugm.model.groups import Groups
from node.ext.ldap.ugm import Ugm


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


# Users container
cone.app.register_plugin('users', Users)


# Groups container
cone.app.register_plugin('groups', Groups)


# The node.ext.ugm implementation to use for user and group management
# currently only LDAP
backend = None


# Flag whether LDAP ugm implementation should be used for authentication
# XXX: move to cone.ldap later
ldap_auth_enabled = False


def initialize_auth_impl(config, global_config, local_config):
    """Initialize LDAP based UGM implementation for cone.app as
    authentication implementation.
    """
    ldap_auth_enabled = local_config.get('cone.ugm.ldap_auth')
    if not ldap_auth_enabled:
        return
    root = cone.app.get_root()
    props = root['settings']['ugm_server'].ldap_props
    ucfg = root['settings']['ugm_users'].ldap_ucfg
    gcfg = root['settings']['ugm_groups'].ldap_gcfg
    ugm = Ugm(name='ldap_ugm', props=props, ucfg=ucfg, gcfg=gcfg)
    cone.app.cfg.auth.append(ugm)


cone.app.register_main_hook(initialize_auth_impl)