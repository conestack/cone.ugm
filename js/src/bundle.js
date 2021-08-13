import $ from 'jquery';
import ts from 'treibstoff';
import {
    PrincipalAdding,
    PrincipalListing
} from './listing.js';

export * from './localmanager.js';
export * from './listing.js';

$(function() {
    ts.ajax.register(PrincipalAdding.initialize, true);
//    ts.ajax.register(ugm.left_listing_nav_binder.bind(ugm), true);
//    ts.ajax.register(ugm.right_listing_nav_binder.bind(ugm), true);
//    ts.ajax.register(ugm.listing_filter_binder.bind(ugm), true);
//    ts.ajax.register(ugm.listing_actions_binder.bind(ugm), true);
//    ts.ajax.register(ugm.listing_related_binder.bind(ugm), true);
});
