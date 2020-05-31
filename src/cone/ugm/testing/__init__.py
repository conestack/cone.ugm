from cone.app import get_root
from cone.app.testing import Security
from cone.app.ugm import ugm_backend
from cone.ugm.settings import ugm_cfg
from node.ext.ldap.testing import LDIF_groupOfNames_10_10
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


class principals_decorator(object):

    @property
    def ugm(self):
        return ugm_backend.ugm

    def create_user(self, user_id, **user_kw):
        self.ugm['users'].create(user_id, **user_kw)

    def create_group(self, group_id, **group_kw):
        self.ugm['groups'].create(group_id, **group_kw)

    def _del_principal(self, principals, name):
        try:
            del principals[name]
        except KeyError:
            # ignore principal. either not created or already removed
            pass

    def del_user(self, name):
        self._del_principal(self.ugm['users'], name)

    def del_group(self, name):
        self._del_principal(self.ugm['groups'], name)

    def invalidate(self):
        root = get_root()
        root['users'].invalidate()
        root['groups'].invalidate()

    def apply(self):
        self.ugm()
        self.invalidate()


class remove_principals(principals_decorator):

    def __init__(self, users=[], groups=[]):
        self.users = users
        self.groups = groups

    def __call__(self, fn):
        def wrapper(inst):
            try:
                fn(inst)
            finally:
                for user_id in self.users:
                    self.del_user(user_id)
                for group_id in self.groups:
                    self.del_group(group_id)
                self.apply()
        return wrapper


class temp_principals(principals_decorator):

    def __init__(self, users={}, groups={}):
        self.users = users
        self.groups = groups

    def __call__(self, fn):
        def wrapper(inst):
            for user_id, user_kw in self.users.items():
                self.create_user(user_id, **user_kw)
            for group_id, group_kw in self.groups.items():
                self.create_group(group_id, **group_kw)
            self.apply()
            try:
                root = get_root()
                fn(inst, root['users'], root['groups'])
            finally:
                for user_id in self.users:
                    self.del_user(user_id)
                for group_id in self.groups:
                    self.del_group(group_id)
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


class UGMLayer(Security, Layer):
    defaultBases = (LDIF_groupOfNames_10_10,)

    def __init__(self):
        Layer.__init__(self)

    def tearDown(self):
        super(UGMLayer, self).tearDown()
        self.cleanup_test_principals()

    def make_app(self):
        super(UGMLayer, self).make_app(**{
            'cone.plugins': 'cone.ldap\ncone.ugm',
            'ugm.backend': 'ldap',
            'ugm.config': ugm_config,
            'ugm.localmanager_config': localmanager_config,
            'ldap.server_config': ldap_server_config,
            'ldap.users_config': ldap_users_config,
            'ldap.groups_config': ldap_groups_config,
            'ldap.roles_config': ldap_roles_config
        })
        self.setup_test_principals()

    def setup_test_principals(self):
        ugm = ugm_backend.ugm
        roles = ['viewer', 'editor', 'admin', 'manager']

        def create_user(uid):
            data = {
                'cn': uid,
                'sn': uid,
                'mail': '%s@example.com' % uid,
            }
            user = ugm.users.create(uid, **data)
            ugm()
            ugm.users.passwd(uid, None, 'secret')
            return user
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp']:
            user = create_user(uid)
            if uid in roles:
                user.add_role(uid)
        for uid in ['localmanager_1', 'localmanager_2']:
            create_user(uid)
        for gid, uid in [
            ('admin_group_1', 'localmanager_1'),
            ('admin_group_2', 'localmanager_2')
        ]:
            group = ugm.groups.create(gid)
            group.add(uid)
        ugm()

    def cleanup_test_principals(self):
        ugm = ugm_backend.ugm
        for uid in [
            'viewer', 'editor', 'admin', 'manager', 'max', 'sepp',
            'localmanager_1', 'localmanager_2'
        ]:
            del ugm.users[uid]
        for gid in ['admin_group_1', 'admin_group_2']:
            del ugm.groups[gid]
        ugm.users()


ugm_layer = UGMLayer()
