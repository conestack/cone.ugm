import sys
import unittest


def test_suite():
    from cone.ugm.tests import test_layout

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_layout))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
