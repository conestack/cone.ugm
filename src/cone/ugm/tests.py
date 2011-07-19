# Copyright 2008-2010, BlueDynamics Alliance, Austria - http://bluedynamics.com
# GNU General Public Licence Version 2 or later

import doctest
import interlude
import pprint
import unittest2 as unittest

# XXX: get rid of plone.testing, use zope test layers directly
from plone.testing import layered, Layer

from cone.app.testing import security
from node.ext.ldap.testing import (
    LDAPLayer,
    LDIF_groupOfNames_10_10,
)


class UGMLayer(Layer):
    defaultBases = (LDIF_groupOfNames_10_10, security)
    
    def setUp(self, args=None):
        self.new_request()
    
    # XXX: better way of providing stuff from base layer below
    
    @property
    def security(self):
        return security
    
    def login(self, login):
        security.login(login)
    
    def logout(self):
        security.logout()
    
    def new_request(self):
        return security.new_request()
    
    @property
    def current_request(self):
        return security.current_request

ugm_layer = UGMLayer()

DOCFILES = [
    ('model/settings.txt', ugm_layer),
    ('model/utils.txt', ugm_layer),
    ('model/users.txt', ugm_layer),
    ('model/user.txt', ugm_layer),
    ('model/groups.txt', ugm_layer),
    ('model/group.txt', ugm_layer),
    ('browser/utils.txt', ugm_layer),
    ('browser/users.txt', ugm_layer),
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
                globs={'interact': interlude.interact,
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
