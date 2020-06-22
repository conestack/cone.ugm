from cone.app import layout_config
from cone.ugm import UGMLayoutConfig
from cone.ugm.model.group import Group
from cone.ugm.model.groups import Groups
from cone.ugm.model.user import User
from cone.ugm.model.users import Users
from pyramid.testing import DummyRequest
import unittest


class TestLayout(unittest.TestCase):

    def test_layout(self):
        config = layout_config.lookup(
            model=Group(None, None, None),
            request=DummyRequest()
        )
        self.assertIsInstance(config, UGMLayoutConfig)

        config = layout_config.lookup(model=Groups(), request=DummyRequest())
        self.assertIsInstance(config, UGMLayoutConfig)

        config = layout_config.lookup(
            model=User(None, None, None),
            request=DummyRequest()
        )
        self.assertIsInstance(config, UGMLayoutConfig)

        config = layout_config.lookup(model=Users(), request=DummyRequest())
        self.assertIsInstance(config, UGMLayoutConfig)

        self.assertTrue(config.mainmenu)
        self.assertFalse(config.mainmenu_fluid)
        self.assertFalse(config.livesearch)
        self.assertTrue(config.personaltools)
        self.assertFalse(config.columns_fluid)
        self.assertFalse(config.pathbar)
        self.assertEqual(config.sidebar_left, [])
        self.assertEqual(config.sidebar_left_grid_width, 0)
        self.assertEqual(config.content_grid_width, 12)
