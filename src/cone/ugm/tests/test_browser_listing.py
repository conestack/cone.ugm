from cone.app import get_root
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.utils import general_settings


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

    def test_listing_items_is_abstract(self):
        listing = ColumnListing()
        self.expectError(NotImplementedError, lambda: listing.listing_items)

    @testing.invalidate_settings
    def test_user_default_sort_column_not_listed(self):
        listing = ColumnListing()
        listing.model = get_root()['users']
        general_settings(listing.model).attrs.users_listing_default_column = 'phone'
        self.assertEqual(listing.user_default_sort_column, 'id')

    @testing.invalidate_settings
    def test_group_default_sort_column_not_listed(self):
        listing = ColumnListing()
        listing.model = get_root()['groups']
        general_settings(listing.model).attrs.groups_listing_default_column = 'phone'
        self.assertEqual(listing.group_default_sort_column, 'id')


class TestBrowserListing(TileTestCase, BrowserListingTests):
    layer = testing.ugm_layer
