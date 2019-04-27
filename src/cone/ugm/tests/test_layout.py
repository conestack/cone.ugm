from cone.ugm.layout import UGMLayout
import unittest


class TestLayout(unittest.TestCase):

    def test_layout(self):
        # Check layout properties
        layout = UGMLayout()
        self.assertTrue(layout.mainmenu)
        self.assertFalse(layout.mainmenu_fluid)
        self.assertFalse(layout.livesearch)
        self.assertTrue(layout.personaltools)
        self.assertFalse(layout.columns_fluid)
        self.assertFalse(layout.pathbar)
        self.assertEqual(layout.sidebar_left, [])
        self.assertEqual(layout.sidebar_left_grid_width, 0)
        self.assertEqual(layout.content_grid_width, 12)
