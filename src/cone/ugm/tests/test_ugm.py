from cone.ugm.testing import ugm_layer
import doctest
import interlude
import pprint
import unittest


DOCFILES = [
    'layout.rst',
    'model/settings.rst',
    'model/utils.rst',
    'model/users.rst',
    'model/groups.rst',
    'model/user.rst',
    'model/group.rst',
    'model/localmanager.rst',
    'browser/__init__.rst',
    'browser/utils.rst',
    'browser/users.rst',
    'browser/groups.rst',
    'browser/root.rst',
    'browser/user.rst',
    'browser/group.rst',
    'browser/actions.rst',
    'browser/settings.rst',
    'browser/remote.rst',
    'browser/expires.rst',
    'browser/roles.rst',
    'browser/autoincrement.rst',
    'browser/portrait.rst',
]


optionflags = (
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS |
    doctest.REPORT_ONLY_FIRST_FAILURE
)


print """
*******************************************************************************
If testing while development fails, please check if memcached is installed and
stop it if running.
*******************************************************************************
"""


def test_suite():
    suite = unittest.TestSuite()
    suite.layer = ugm_layer
    globs = {
        'interact': interlude.interact,
        'pprint': pprint.pprint,
        'pp': pprint.pprint,
        'layer': ugm_layer
    }
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            globs=globs,
            optionflags=optionflags
        )
        for docfile in DOCFILES
    ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
