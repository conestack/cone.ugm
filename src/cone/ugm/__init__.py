from cone.app import get_root
from cone.app.security import acl_registry
from cone.app.ugm import ugm_backend
from cone.app.ugm import UGMBackend
from cone.ugm.browser import static_resources
from cone.ugm.model.group import Group
from cone.ugm.model.groups import Groups
from cone.ugm.model.groups import groups_factory
from cone.ugm.model.settings import GeneralSettings
from cone.ugm.model.settings import GroupsSettings
from cone.ugm.model.settings import LocalManagerSettings
from cone.ugm.model.settings import RolesSettings
from cone.ugm.model.settings import ServerSettings
from cone.ugm.model.settings import UsersSettings
from cone.ugm.model.user import User
from cone.ugm.model.users import Users
from cone.ugm.model.users import users_factory
from node.ext.ldap.ugm import Ugm as LdapUgm
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import Everyone
import cone.app
import logging
import os


logger = logging.getLogger('cone.ugm')


# custom UGM styles
cone.app.cfg.merged.css.protected.append((static_resources, 'styles.css'))

# custom UGM javascript
cone.app.cfg.merged.js.protected.append(
    (static_resources, 'jQuery.sortElements.js')
)
cone.app.cfg.merged.js.protected.append((static_resources, 'naturalSort.js'))
cone.app.cfg.merged.js.protected.append((static_resources, 'ugm.js'))

# UGM settings
cone.app.register_plugin_config('ugm_general', GeneralSettings)
cone.app.register_plugin_config('ugm_server', ServerSettings)
cone.app.register_plugin_config('ugm_users', UsersSettings)
cone.app.register_plugin_config('ugm_groups', GroupsSettings)
cone.app.register_plugin_config('ugm_roles', RolesSettings)
cone.app.register_plugin_config('ugm_localmanager', LocalManagerSettings)

# Users container
cone.app.register_plugin('users', users_factory)

# Groups container
cone.app.register_plugin('groups', groups_factory)

# security
management_permissions = [
    'add', 'edit', 'delete',
]
user_management_permissions = [
    'add_user', 'edit_user', 'delete_user', 'manage_expiration',
]
group_management_permissions = [
    'add_group', 'edit_group', 'delete_group',
]
admin_permissions = [
    'view', 'manage_membership', 'view_portrait',
] + management_permissions \
  + user_management_permissions \
  + group_management_permissions
ugm_default_acl = [
    (Allow, 'role:editor', ['view', 'manage_membership']),
    (Allow, 'role:admin', admin_permissions),
    (Allow, 'role:manager', admin_permissions + ['manage']),
    (Allow, Everyone, ['login']),
    (Deny, Everyone, ALL_PERMISSIONS),
]
ugm_user_acl = [
    (Allow, 'system.Authenticated', ['view_portrait']),
] + ugm_default_acl

# register default acl's
# XXX: define permissions referring users, user, groups respective group only,
acl_registry.register(ugm_user_acl, User, 'user')
acl_registry.register(ugm_default_acl, Users, 'users')
acl_registry.register(ugm_default_acl, Group, 'group')
acl_registry.register(ugm_default_acl, Groups, 'groups')


# application startup hooks
@cone.app.main_hook
def initialize_ugm(config, global_config, local_config):
    """Initialize UGM.
    """
    # localmanager config file location
    lm_config = local_config.get('ugm.localmanager_config', '')
    os.environ['LOCAL_MANAGER_CFG_FILE'] = lm_config

    # add translation
    config.add_translation_dirs('cone.ugm:locale/')

    # static resources
    config.add_view(static_resources, name='cone.ugm.static')

    # scan browser package
    config.scan('cone.ugm.browser')


###############################################################################
# XXX: move to cone.ldap
###############################################################################

@cone.app.main_hook
def initialize_ldap(config, global_config, local_config):
    """Initialize cone.ldap.
    """
    os.environ['LDAP_CFG_FILE'] = local_config.get('ldap.config', '')


@ugm_backend('ldap')
class LDAPUGMBackend(UGMBackend):
    """UGM backend factory for file based UGM implementation.
    """

    def __init__(self, settings):
        self.users_file = settings.get('ugm.users_file')
        self.groups_file = settings.get('ugm.groups_file')
        self.roles_file = settings.get('ugm.roles_file')
        self.datadir = settings.get('ugm.datadir')

    def __call__(self):
        settings = get_root()['settings']
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
        return LdapUgm(
            name='ldap_ugm',
            props=props,
            ucfg=ucfg,
            gcfg=gcfg,
            rcfg=rcfg
        )
