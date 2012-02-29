import os
import doctest
import interlude
import pprint
import pkg_resources
import unittest2 as unittest

from plone.testing import layered

from cone.app.testing import Security
from node.ext.ldap.testing import (
    LDAPLayer,
    LDIF_groupOfNames_10_10,
)


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
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp']:
            data = {
                'cn': uid,
                'sn': uid,
                'mail': '%s@example.com' % uid,
            }
            user = ugm.users.create(uid, **data)
            ugm()
            ugm.users.passwd(uid, None, 'secret')
            if uid in roles:
                user.add_role(uid)
        ugm()
    
    def tearDown(self):
        super(UGMLayer, self).tearDown()
        import cone.app
        ugm = cone.app.cfg.auth
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp']:
            del ugm.users[uid]
        ugm.users()
    
    def make_app(self):
        ldap_config = os.path.join(os.path.split(__file__)[0], 'ldap.xml')
        super(UGMLayer, self).make_app(**{
            'cone.auth_impl': 'node.ext.ldap',
            'cone.plugins': 'node.ext.ugm\ncone.ugm',
            'cone.ugm.ldap_config': ldap_config,
        })
        LDIF_groupOfNames_10_10.gcfg.attrmap['cn'] = 'cn'


ugm_layer = UGMLayer()


DOCFILES = [
    ('../model/settings.rst', ugm_layer),
    ('../model/utils.rst', ugm_layer),
    ('../model/users.rst', ugm_layer),
    ('../model/groups.rst', ugm_layer),
    ('../model/user.rst', ugm_layer),
    ('../model/group.rst', ugm_layer),
    ('../browser/__init__.rst', ugm_layer),
    ('../browser/utils.rst', ugm_layer),
    ('../browser/users.rst', ugm_layer),
    ('../browser/groups.rst', ugm_layer),
    ('../browser/root.rst', ugm_layer),
    ('../browser/user.rst', ugm_layer),
    ('../browser/group.rst', ugm_layer),
    ('../browser/actions.rst', ugm_layer),
    ('../browser/settings.rst', ugm_layer),
    ('../browser/remote.rst', ugm_layer),
    ('../browser/expires.rst', ugm_layer),
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