from cone.app.ugm import ugm_backend
from cone.ugm import testing
from node.tests import NodeTestCase
from types import SimpleNamespace
from unittest import mock
import unittest


class FailingPrincipals(dict):
    """Principals container raising ``error`` on deletion."""

    def __init__(self, error, *principal_ids):
        super().__init__((principal_id, None) for principal_id in principal_ids)
        self.error = error

    def __delitem__(self, key):
        raise self.error

    def __call__(self):
        """Nothing to persist."""


class TestPrincipals(unittest.TestCase):
    def _remove_principals(self, error):
        ugm = SimpleNamespace(
            users=FailingPrincipals(error, 'user_1'),
            groups=FailingPrincipals(error, 'group_1'),
        )
        with (
            mock.patch.object(testing, 'ugm_backend', SimpleNamespace(ugm=ugm)),
            mock.patch.object(testing.principals, 'apply'),
            mock.patch('builtins.print') as print_,
        ):
            testing.principals().remove_principals()
        return print_

    def test_remove_principals_skips_missing_principals(self):
        print_ = self._remove_principals(KeyError('missing'))
        print_.assert_not_called()

    def test_remove_principals_reports_failures(self):
        print_ = self._remove_principals(Exception('failed'))
        self.assertEqual(
            print_.call_args_list,
            [
                mock.call(
                    'Error while removing user. Please check underlying UGM '
                    'implementation: failed'
                ),
                mock.call(
                    'Error while removing group. Please check underlying UGM '
                    'implementation: failed'
                ),
            ],
        )

    def test_principals_raises_failure_while_removing_principals(self):
        principals = testing.principals()
        decorated = principals(lambda inst: None)
        with (
            mock.patch.object(principals, 'create_principals'),
            mock.patch.object(
                principals, 'remove_principals', side_effect=Exception('failed')
            ),
        ):
            with self.assertRaises(Exception) as context:
                decorated(None)
        self.assertEqual(str(context.exception), 'failed')


class TestPrincipalsDecorator(NodeTestCase):
    layer = testing.ugm_layer

    @testing.principals(groups={'group_1': {}}, roles={'group:group_1': ['editor']})
    def test_group_roles(self):
        self.assertEqual(ugm_backend.ugm.groups['group_1'].roles, ['editor'])
