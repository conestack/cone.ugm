from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.listing import ColumnListing


class BrowserListingTests:

    def test_unquoted_param_value(self):
        listing = ColumnListing()
        listing.request = self.layer.new_request()
        self.assertEqual(listing.unquoted_param_value('filter'), None)

        listing.request.params['filter'] = 'M%C3%BCller%20%2A'
        self.assertEqual(listing.unquoted_param_value('filter'), 'Müller *')

    def test_extract_raw(self):
        listing = ColumnListing()
        attrs = {
            'list': ['a', 'b'],
            'tuple': ('c', 'd'),
            'str': 'e',
            'none': None,
        }
        self.assertEqual(listing.extract_raw(attrs, 'list'), 'a')
        self.assertEqual(listing.extract_raw(attrs, 'tuple'), 'c')
        self.assertEqual(listing.extract_raw(attrs, 'str'), 'e')
        self.assertEqual(listing.extract_raw(attrs, 'none'), '')
        self.assertEqual(listing.extract_raw(attrs, 'missing'), '')


class TestBrowserListing(TileTestCase, BrowserListingTests):
    layer = testing.ugm_layer
