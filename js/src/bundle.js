import $ from 'jquery';
import ts from 'treibstoff';
import {PrincipalListing} from './listing.js';

export * from './actions.js';
export * from './listing.js';
export * from './localmanager.js';

$(function() {
    ts.ajax.register(PrincipalListing.initialize, true);
});
