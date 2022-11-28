from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.utils import quote_slash
from cone.ugm.browser.utils import unquote_slash


class TestBrowserUtilsBase(object):

    def test_utils(self):
        quoted = quote_slash('foo/bar')
        self.assertEqual(quoted, 'foo__s_l_a_s_h__bar')
        self.assertEqual(unquote_slash(quoted), 'foo/bar')


class TestBrowserUtils(TileTestCase, TestBrowserUtilsBase):
    layer = testing.ugm_layer
