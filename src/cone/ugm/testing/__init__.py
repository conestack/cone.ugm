from cone.app import get_root
from cone.app.testing import Security
from cone.app.ugm import ugm_backend
from cone.ugm.settings import ugm_cfg
import os
import shutil
import tempfile


base_path = os.path.split(__file__)[0]
ugm_config = os.path.join(base_path, 'ugm.xml')
localmanager_config = os.path.join(base_path, 'localmanager.xml')


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

    def create_principals(self):
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
        for principal_id, roles in self.roles.items():
            if principal_id.startswith('group:'):
                principal = ugm_groups[principal_id[5:]]
            else:
                principal = ugm_users[principal_id]
            for role in roles:
                principal.add_role(role)
        self.apply()

    def remove_principals(self):
        ugm = ugm_backend.ugm
        ugm_users = ugm.users
        ugm_groups = ugm.groups
        for user_id in ugm_users.keys():
            try:
                del ugm_users[user_id]
                ugm_users()
            except KeyError:
                continue
            except Exception as e:
                print((
                    'Error while removing user. Please '
                    'check underlying UGM implementation: {}'
                ).format(e))
        for group_id in ugm_groups.keys():
            try:
                del ugm_groups[group_id]
                ugm_groups()
            except KeyError:
                continue
            except Exception as e:
                print((
                    'Error while removing group. Please '
                    'check underlying UGM implementation: {}'
                ).format(e))
        self.apply()

    def __call__(self, fn):
        def wrapper(inst):
            self.create_principals()
            try:
                fn(inst)
            finally:
                try:
                    self.remove_principals()
                except Exception as e:
                    raise e
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


class UGMLayer(Security):

    def make_app(self):
        ugm_users_file = os.path.join(self.ugm_dir, 'users')
        ugm_groups_file = os.path.join(self.ugm_dir, 'groups')
        ugm_roles_file = os.path.join(self.ugm_dir, 'roles')
        ugm_datadir = os.path.join(self.ugm_dir, 'data')
        super(UGMLayer, self).make_app(**{
            'cone.plugins': '\n'.join([
                'cone.ugm'
            ]),
            'ugm.backend': 'file',
            'ugm.config': ugm_config,
            'ugm.localmanager_config': localmanager_config,
            'ugm.users_file': ugm_users_file,
            'ugm.groups_file': ugm_groups_file,
            'ugm.roles_file': ugm_roles_file,
            'ugm.datadir': ugm_datadir
        })
        ugm_backend.initialize()

    def setUp(self, args=None):
        self.ugm_dir = tempfile.mkdtemp()
        super(UGMLayer, self).setUp(args=args)

    def tearDown(self):
        shutil.rmtree(self.ugm_dir)
        super(UGMLayer, self).tearDown()


ugm_layer = UGMLayer()
