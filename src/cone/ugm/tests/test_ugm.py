from cone.app.testing import Security
from node.ext.ldap.testing import LDIF_groupOfNames_10_10
from plone.testing import layered
import doctest
import interlude
import os
import pkg_resources
import pprint
import unittest2 as unittest


class UGMLayer(Security):
    defaultBases = (LDIF_groupOfNames_10_10, )

    def setUp(self, args=None):
        super(UGMLayer, self).setUp(args)
        import cone.ugm
        path = pkg_resources.resource_filename('cone.ugm.tests', 'ldap.xml')
        cone.ugm.model.utils.LDAP_CFG_FILE = path
        cone.ugm.model.settings._invalidate_ugm_settings(cone.app.get_root())
        ugm = cone.ugm.model.utils.ugm_backend(cone.app.get_root())
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
        import cone.app
        ugm = cone.app.cfg.auth
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
            'cone.auth_impl': 'node.ext.ldap',
            'cone.plugins': 'node.ext.ugm\ncone.ugm',
            'cone.ugm.ldap_config': ldap_config,
            'cone.ugm.localmanager_config': localmanager_config,
        })
        LDIF_groupOfNames_10_10.gcfg.attrmap['cn'] = 'cn'


ugm_layer = UGMLayer()


DOCFILES = [
    ('../layout.rst', ugm_layer),
    ('../model/settings.rst', ugm_layer),
    ('../model/utils.rst', ugm_layer),
    ('../model/users.rst', ugm_layer),
    ('../model/groups.rst', ugm_layer),
    ('../model/user.rst', ugm_layer),
    ('../model/group.rst', ugm_layer),
    ('../model/localmanager.rst', ugm_layer),
    ('../browser/__init__.rst', ugm_layer),
    ('../browser/utils.rst', ugm_layer),
    ('../browser/users.rst', ugm_layer),
    ('../browser/groups.rst', ugm_layer),
    #('../browser/root.rst', ugm_layer),
    #('../browser/user.rst', ugm_layer),
    #('../browser/group.rst', ugm_layer),
    #('../browser/actions.rst', ugm_layer),
    #('../browser/settings.rst', ugm_layer),
    #('../browser/remote.rst', ugm_layer),
    #('../browser/expires.rst', ugm_layer),
    #('../browser/roles.rst', ugm_layer),
    #('../browser/autoincrement.rst', ugm_layer),
    #('../browser/portrait.rst', ugm_layer),
]


optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE


print """
*******************************************************************************
If testing while development fails, please check if memcached is installed and
stop it if running.
*******************************************************************************
"""


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                docfile,
                globs={
                    'interact': interlude.interact,
                    'pprint': pprint.pprint,
                    'pp': pprint.pprint,
                    },
                optionflags=optionflags,
                ),
            layer=layer,
            )
        for docfile, layer in DOCFILES
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE
