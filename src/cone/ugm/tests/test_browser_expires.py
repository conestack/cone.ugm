from cone.tile.tests import TileTestCase
from cone.ugm import testing


class BrowserExpiresTests(object):

    def test_expiration_widget(self):
        pass


class TestBrowserExpires(TileTestCase, BrowserExpiresTests):
    layer = testing.ugm_layer
