import * as actions from './actions.js';
import * as listing from './listing.js';

const api = {};

Object.assign(api, actions);
Object.assign(api, listing);

const ugm = api;
export default ugm;
