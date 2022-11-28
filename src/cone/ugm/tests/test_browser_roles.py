from cone.tile.tests import TileTestCase
from cone.ugm import testing


class TestBrowserRolesBase(object):

    def test_roles(self):
        pass


class TestBrowserRoles(TileTestCase, TestBrowserRolesBase):
    layer = testing.ugm_layer
