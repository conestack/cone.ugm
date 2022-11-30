from cone.tile.tests import TileTestCase
from cone.ugm import testing


class TestBrowserExpiresBase(object):

    def test_expiration_widget(self):
        pass


class TestBrowserExpires(TileTestCase, TestBrowserExpiresBase):
    layer = testing.ugm_layer
