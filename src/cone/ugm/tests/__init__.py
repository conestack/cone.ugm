import sys
import unittest


def test_suite():
    from cone.ugm.tests import test_layout

    from cone.ugm.tests import test_model_group
    from cone.ugm.tests import test_model_groups
    from cone.ugm.tests import test_model_localmanager
    from cone.ugm.tests import test_model_settings
    from cone.ugm.tests import test_model_user
    from cone.ugm.tests import test_model_users
    from cone.ugm.tests import test_model_utils

    from cone.ugm.tests import test_browser_actions
    from cone.ugm.tests import test_browser_autoincrement
    from cone.ugm.tests import test_browser_expires
    from cone.ugm.tests import test_browser_group
    from cone.ugm.tests import test_browser_groups
    from cone.ugm.tests import test_browser_portrait
    from cone.ugm.tests import test_browser_remote
    from cone.ugm.tests import test_browser_roles
    from cone.ugm.tests import test_browser_root

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_layout))

    suite.addTest(unittest.findTestCases(test_model_group))
    suite.addTest(unittest.findTestCases(test_model_groups))
    suite.addTest(unittest.findTestCases(test_model_localmanager))
    suite.addTest(unittest.findTestCases(test_model_settings))
    suite.addTest(unittest.findTestCases(test_model_user))
    suite.addTest(unittest.findTestCases(test_model_users))
    suite.addTest(unittest.findTestCases(test_model_utils))

    suite.addTest(unittest.findTestCases(test_browser_actions))
    suite.addTest(unittest.findTestCases(test_browser_autoincrement))
    suite.addTest(unittest.findTestCases(test_browser_expires))
    suite.addTest(unittest.findTestCases(test_browser_group))
    suite.addTest(unittest.findTestCases(test_browser_groups))
    suite.addTest(unittest.findTestCases(test_browser_portrait))
    suite.addTest(unittest.findTestCases(test_browser_remote))
    suite.addTest(unittest.findTestCases(test_browser_roles))
    suite.addTest(unittest.findTestCases(test_browser_root))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
