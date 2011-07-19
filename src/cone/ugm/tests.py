import os
import doctest
import interlude
import pprint
import unittest2 as unittest

# XXX: get rid of plone.testing, use zope test layers directly
from plone.testing import layered, Layer

from cone.app.testing import Security, DATADIR
from node.ext.ldap.testing import (
    LDAPLayer,
    LDIF_groupOfNames_10_10,
)


class UGMLayer(Security):
    defaultBases = (LDIF_groupOfNames_10_10, )
    
    def make_app(self):
        super(UGMLayer, self).make_app(**{
            'cone.plugins': 'node.ext.ugm\ncone.ugm',
        })
        LDIF_groupOfNames_10_10.gcfg.attrmap['cn'] = 'cn'


ugm_layer = UGMLayer()


DOCFILES = [
    ('model/settings.txt', ugm_layer),
    ('model/utils.txt', ugm_layer),
    ('model/users.txt', ugm_layer),
    ('model/groups.txt', ugm_layer),
    ('model/user.txt', ugm_layer),
    ('model/group.txt', ugm_layer),
    ('browser/__init__.txt', ugm_layer),
    ('browser/utils.txt', ugm_layer),
    ('browser/users.txt', ugm_layer),
    ('browser/groups.txt', ugm_layer),
    ('browser/root.txt', ugm_layer),
    ('browser/user.txt', ugm_layer),
    ('browser/group.txt', ugm_layer),
    ('browser/actions.txt', ugm_layer),
    ('browser/settings.txt', ugm_layer),
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
    unittest.main(defaultTest='test_suite')
