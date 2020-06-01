from cone.app import get_root
from cone.app.testing import Security
from cone.app.ugm import ugm_backend
from cone.ugm.settings import ugm_cfg
from node.ext.ldap.testing import LDIF_base
from node.ext.ldap.ugm.defaults import creation_defaults
from plone.testing import Layer
import os
import shutil
import tempfile


base_path = os.path.split(__file__)[0]
ugm_config = os.path.join(base_path, 'ugm.xml')
localmanager_config = os.path.join(base_path, 'localmanager.xml')
ldap_server_config = os.path.join(base_path, 'ldap_server.xml')
ldap_users_config = os.path.join(base_path, 'ldap_users.xml')
ldap_groups_config = os.path.join(base_path, 'ldap_groups.xml')
ldap_roles_config = os.path.join(base_path, 'ldap_roles.xml')


class principals(object):

    def __init__(self, users={}, groups={}, membership={}, roles={}):
        self.users = users
        self.groups = groups
        self.membership = membership
        self.roles = roles

    def apply(self):
        ugm_backend.ugm()
        root = get_root()
        root['users'].invalidate()
        root['groups'].invalidate()

    def __call__(self, fn):
        def wrapper(inst):
            ugm = ugm_backend.ugm
            ugm_users = ugm.users
            ugm_groups = ugm.groups
            for user_id, user_kw in self.users.items():
                ugm_users.create(user_id, **user_kw)
                ugm_users()
                ugm_users.passwd(user_id, None, 'secret')
            for group_id, group_kw in self.groups.items():
                ugm_groups.create(group_id, **group_kw)
            for group_id, user_ids in self.membership.items():
                ugm_group = ugm_groups[group_id]
                for user_id in user_ids:
                    ugm_group.add(user_id)
            for principal_id, roles in self.roles:
                if principal_id.startswith('group:'):
                    principal = ugm_groups[principal_id[5:]]
                else:
                    principal = ugm_users[principal_id]
                for role in roles:
                    principal.add_role(role)
            self.apply()
            try:
                fn(inst)
            finally:
                for user_id in self.users:
                    try:
                        del ugm_users[user_id]
                        ugm_users()
                    except KeyError:
                        continue
                for group_id in self.groups:
                    try:
                        del ugm_groups[group_id]
                        ugm_groups()
                    except KeyError:
                        continue
                self.apply()
        return wrapper


def _invalidate_settings():
    settings = get_root()['settings']
    settings['ugm_general'].invalidate()


def invalidate_settings(fn):
    """Decorator for tests working on settings nodes.
    """
    def wrapper(*a, **kw):
        _invalidate_settings()
        try:
            fn(*a, **kw)
        finally:
            _invalidate_settings()
    return wrapper


def custom_config_path(fn):
    """Decorator for tests writing to config files.
    """
    def wrapper(*a, **kw):
        ugm_settings = ugm_cfg.ugm_settings
        _invalidate_settings()
        try:
            fn(*a, **kw)
        finally:
            ugm_cfg.ugm_settings = ugm_settings
            _invalidate_settings()
    return wrapper


def temp_directory(fn):
    """Decorator for tests needing a temporary directory.
    """
    def wrapper(*a, **kw):
        tempdir = tempfile.mkdtemp()
        kw['tempdir'] = tempdir
        try:
            fn(*a, **kw)
        finally:
            shutil.rmtree(tempdir)
    return wrapper


def rdn_value(node, uid):
    return uid.split('=')[1]


def create_mail(node, uid):
    return '%s@example.com' % rdn_value(node, uid)


creation_defaults['inetOrgPerson'] = dict()
creation_defaults['inetOrgPerson']['sn'] = rdn_value
creation_defaults['inetOrgPerson']['cn'] = rdn_value
creation_defaults['inetOrgPerson']['mail'] = create_mail


class UGMLayer(Security, Layer):
    defaultBases = (LDIF_base,)

    def __init__(self):
        Layer.__init__(self)

    def tearDown(self):
        super(UGMLayer, self).tearDown()

    def make_app(self):
        super(UGMLayer, self).make_app(**{
            'cone.plugins': '\n'.join([
                'cone.ldap',
                'cone.ugm'
            ]),
            'ugm.backend': 'ldap',
            'ugm.config': ugm_config,
            'ugm.localmanager_config': localmanager_config,
            'ldap.server_config': ldap_server_config,
            'ldap.users_config': ldap_users_config,
            'ldap.groups_config': ldap_groups_config,
            'ldap.roles_config': ldap_roles_config
        })
        settings = get_root()['settings']
        settings['ldap_users'].create_container()
        settings['ldap_groups'].create_container()
        settings['ldap_roles'].create_container()
        ugm_backend.initialize()


ugm_layer = UGMLayer()
