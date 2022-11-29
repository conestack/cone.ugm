from cone.tile.tests import TileTestCase
from cone.ugm import testing
from datetime import datetime
from node.utils import UNSET
from yafowil.base import factory
import time


class TestBrowserExpiresBase(object):

    def test_expiration_widget(self):
        pass


class TestBrowserExpires(TileTestCase, TestBrowserExpiresBase):
    layer = testing.ugm_layer
