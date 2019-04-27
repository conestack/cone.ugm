from cone.app import root
from cone.app.testing import Security
from cone.app.ugm import ugm_backend
from node.ext.ldap.testing import LDIF_groupOfNames_10_10
from plone.testing import Layer
import os
import pkg_resources


class temp_principals(object):

    def __init__(self, users={}, groups={}):
        self.users = users
        self.groups = groups

    def __call__(self, fn):
        def wrapper(inst):
            ugm = ugm_backend.ugm
            for user_id, user_kw in self.users.items():
                ugm['users'].create(user_id, **user_kw)
            for group_id, group_kw in self.groups.items():
                ugm['groups'].create(group_id, **group_kw)
            ugm()
            root['users'].invalidate()
            root['groups'].invalidate()
            try:
                fn(inst, root['users'], root['groups'])
            finally:
                root['users'].invalidate()
                root['groups'].invalidate()
                ugm = ugm_backend.ugm
                for user_id in self.users:
                    try:
                        del ugm['users'][user_id]
                    except KeyError:
                        # ignore, user_id already deleted
                        pass
                for group_id in self.groups:
                    try:
                        del ugm['groups'][group_id]
                    except KeyError:
                        # ignore, group_id already deleted
                        pass
                ugm()
        return wrapper


class UGMLayer(Security, Layer):
    defaultBases = (LDIF_groupOfNames_10_10,)

    def __init__(self):
        Layer.__init__(self)

    def setUp(self, args=None):
        super(UGMLayer, self).setUp(args)
        path = pkg_resources.resource_filename('cone.ugm.testing', 'ldap.xml')
        ugm_backend.load('ldap', {'ldap.config': path})
        ugm_backend.initialize()
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
        for gid, uid in [('admin_group_1', 'localmanager_1'),
                         ('admin_group_2', 'localmanager_2')]:
            group = ugm.groups.create(gid)
            group.add(uid)
        ugm()

    def tearDown(self):
        super(UGMLayer, self).tearDown()
        ugm = ugm_backend.ugm
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp',
                    'localmanager_1', 'localmanager_2']:
            del ugm.users[uid]
        for gid in ['admin_group_1', 'admin_group_2']:
            del ugm.groups[gid]
        ugm.users()

    def make_app(self):
        base_path = os.path.split(__file__)[0]
        ldap_config = os.path.join(base_path, 'ldap.xml')
        localmanager_config = os.path.join(base_path, 'localmanager.xml')
        super(UGMLayer, self).make_app(**{
            'cone.plugins': 'cone.ugm',
            'ugm.backend': 'ldap',
            'ugm.localmanager_config': localmanager_config,
            'ldap.config': ldap_config,
        })


ugm_layer = UGMLayer()
