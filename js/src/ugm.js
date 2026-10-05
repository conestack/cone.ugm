import * as actions from './actions.js';
import * as listing from './listing.js';

let api = {};

Object.assign(api, actions);
Object.assign(api, listing);

let ugm = api;
export default ugm;
