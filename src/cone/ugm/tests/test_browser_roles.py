from cone.tile.tests import TileTestCase
from cone.ugm import testing


class BrowserRolesTests:

    def test_roles(self):
        pass


class TestBrowserRoles(TileTestCase, BrowserRolesTests):
    layer = testing.ugm_layer
