import sys
import unittest


def test_suite():
    from cone.ugm.tests import test_layout
    from cone.ugm.tests import test_localmanager
    from cone.ugm.tests import test_settings
    from cone.ugm.tests import test_utils

    from cone.ugm.tests import test_model_group
    from cone.ugm.tests import test_model_groups
    from cone.ugm.tests import test_model_user
    from cone.ugm.tests import test_model_users

    from cone.ugm.tests import test_browser_actions
    from cone.ugm.tests import test_browser_autoincrement
    from cone.ugm.tests import test_browser_expires
    from cone.ugm.tests import test_browser_group
    from cone.ugm.tests import test_browser_groups
    from cone.ugm.tests import test_browser_password
    from cone.ugm.tests import test_browser_portrait
    from cone.ugm.tests import test_browser_principal
    from cone.ugm.tests import test_browser_remote
    from cone.ugm.tests import test_browser_roles
    from cone.ugm.tests import test_browser_root
    from cone.ugm.tests import test_browser_settings
    from cone.ugm.tests import test_browser_user
    from cone.ugm.tests import test_browser_users
    from cone.ugm.tests import test_browser_utils

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_layout))
    suite.addTest(unittest.findTestCases(test_localmanager))
    suite.addTest(unittest.findTestCases(test_settings))
    suite.addTest(unittest.findTestCases(test_utils))

    suite.addTest(unittest.findTestCases(test_model_group))
    suite.addTest(unittest.findTestCases(test_model_groups))
    suite.addTest(unittest.findTestCases(test_model_user))
    suite.addTest(unittest.findTestCases(test_model_users))

    suite.addTest(unittest.findTestCases(test_browser_actions))
    suite.addTest(unittest.findTestCases(test_browser_autoincrement))
    suite.addTest(unittest.findTestCases(test_browser_expires))
    suite.addTest(unittest.findTestCases(test_browser_group))
    suite.addTest(unittest.findTestCases(test_browser_groups))
    suite.addTest(unittest.findTestCases(test_browser_password))
    suite.addTest(unittest.findTestCases(test_browser_portrait))
    suite.addTest(unittest.findTestCases(test_browser_principal))
    suite.addTest(unittest.findTestCases(test_browser_remote))
    suite.addTest(unittest.findTestCases(test_browser_roles))
    suite.addTest(unittest.findTestCases(test_browser_root))
    suite.addTest(unittest.findTestCases(test_browser_settings))
    suite.addTest(unittest.findTestCases(test_browser_user))
    suite.addTest(unittest.findTestCases(test_browser_users))
    suite.addTest(unittest.findTestCases(test_browser_utils))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
