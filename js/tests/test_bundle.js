import $ from 'jquery';
import ts from 'treibstoff';
import * as actions from '../src/actions.js';
import * as listing from '../src/listing.js';
import ugm from '../src/ugm.js';

const api_names = [
    'LeftPrincipalListing',
    'PrincipalActions',
    'PrincipalListing',
    'RightPrincipalListing',
];

QUnit.module('cone.ugm.bundle', (hooks) => {
    const ts_ajax_register_origin = ts.ajax.register;

    hooks.afterEach(() => {
        ts.ajax.register = ts_ajax_register_origin;
    });

    QUnit.test('bundle exports ugm API and registers listing on DOM ready', async (assert) => {
        const registered = [];
        ts.ajax.register = (func, instant) => {
            registered.push({ func, instant });
        };

        const bundle = await import('../src/bundle.js');
        // ready callbacks run in registration order, this one after the bundle's
        await new Promise((resolve) => $(resolve));

        assert.deepEqual(Object.keys(bundle).sort(), api_names, 'exported names');
        assert.strictEqual(registered.length, 1, 'one registration');
        assert.strictEqual(
            registered[0].func,
            bundle.PrincipalListing.initialize,
            'initialize registered',
        );
        assert.true(registered[0].instant, 'registered for instant execution');
    });
});

QUnit.module('cone.ugm.ugm', () => {
    QUnit.test('ugm namespace contains actions and listing API', (assert) => {
        assert.deepEqual(Object.keys(ugm).sort(), api_names, 'API names');
        assert.strictEqual(ugm.PrincipalActions, actions.PrincipalActions);
        assert.strictEqual(ugm.PrincipalListing, listing.PrincipalListing);
        assert.strictEqual(ugm.LeftPrincipalListing, listing.LeftPrincipalListing);
        assert.strictEqual(ugm.RightPrincipalListing, listing.RightPrincipalListing);
    });
});
