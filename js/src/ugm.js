import * as actions from './actions.js';
import * as listing from './listing.js';
import * as localmanager from './localmanager.js';

let api = {};

Object.assign(api, actions);
Object.assign(api, listing);
Object.assign(api, localmanager);

let ugm = api;
export default ugm;
