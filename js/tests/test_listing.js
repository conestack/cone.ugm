import cone from 'cone';
import $ from 'jquery';
import ts from 'treibstoff';
import { PrincipalActions } from '../src/actions.js';
import { LeftPrincipalListing, PrincipalListing, RightPrincipalListing } from '../src/listing.js';

function setup_listing_hooks(hooks) {
    const origin = {};

    hooks.beforeEach(function () {
        this.container = $('<div />').appendTo('body');
        origin.batched_items_search = cone.BatchedItemsSearch.initialize;
        origin.action = ts.ajax.action;
        origin.trigger = ts.ajax.trigger;
        origin.request = ts.ajax.request;
        origin.show_dialog = ts.show_dialog;
        const assert = QUnit.config.current.assert;
        ts.ajax.action = (opts) => {
            assert.step(`action ${opts.name} ${opts.selector} ${opts.mode} ${opts.url}`);
            assert.step(`params ${JSON.stringify(opts.params)}`);
        };
        ts.ajax.trigger = (name, selector, target) => {
            assert.step(`trigger ${name} ${selector} ${target}`);
        };
        ts.ajax.request = (opts) => {
            assert.step(`request ${opts.url}`);
        };
        ts.show_dialog = (opts) => {
            assert.step(`dialog ${opts.title}`);
        };
    });

    hooks.afterEach(function () {
        cone.BatchedItemsSearch.initialize = origin.batched_items_search;
        ts.ajax.action = origin.action;
        ts.ajax.trigger = origin.trigger;
        ts.ajax.request = origin.request;
        ts.show_dialog = origin.show_dialog;
        this.container.remove();
    });
}

function create_left_column(container) {
    return $(`
        <div class="left_column">
          <div class="add_button">
            <button ajax:target="http://tld.com/users?type=user">Add</button>
          </div>
          <div class="columnitems">
            <ul class="leftlisting">
              <li ajax:target="http://tld.com/users/user1?a=1">
                <div class="cols"><div class="sort_col_1">user1</div></div>
                <div class="actions">
                  <a class="delete_item" ajax:target="http://tld.com/users/user1">x</a>
                </div>
              </li>
              <li ajax:target="http://tld.com/users/user2" class="selected">
                <div class="cols"><div class="sort_col_1">user2</div></div>
                <div class="actions">
                  <a class="delete_item_disabled">x</a>
                </div>
              </li>
            </ul>
          </div>
        </div>
    `).appendTo(container);
}

function create_right_column(container) {
    return $(`
        <div class="right_column">
          <div class="column_limit">
            <input type="checkbox"
                   class="list_all"
                   ajax:target="http://tld.com/users/user1?b=2" />
          </div>
          <div class="columnitems">
            <ul class="rightlisting">
              <li ajax:target="http://tld.com/groups/group1">
                <div class="actions">
                  <a class="add_item" ajax:target="http://tld.com/groups/group1?id=user1">+</a>
                  <a class="remove_item_disabled">-</a>
                </div>
              </li>
              <li ajax:target="http://tld.com/groups/group2" class="selected">
                <div class="actions">
                  <a class="add_item_disabled">+</a>
                  <a class="remove_item" ajax:target="http://tld.com/groups/group2?id=user1">-</a>
                </div>
              </li>
            </ul>
          </div>
        </div>
    `).appendTo(container);
}

QUnit.module('cone.ugm.listing.PrincipalListing', (hooks) => {
    setup_listing_hooks(hooks);

    QUnit.test('initialize', function (assert) {
        const left = create_left_column(this.container);
        const right = create_right_column(this.container);
        cone.BatchedItemsSearch.initialize = (context, selector, name) => {
            assert.step(`batched items search ${selector} ${name}`);
            assert.strictEqual(context, this.container);
        };

        PrincipalListing.initialize(this.container);
        assert.verifySteps(['batched items search div.column_filter input filter']);

        // left and right listings are bound
        $('ul.leftlisting li', left).first().trigger('click');
        $('ul.rightlisting li', right).first().trigger('click');
        assert.verifySteps([
            'action rightcolumn .right_column replace http://tld.com/users/user1',
            'params {"a":"1"}',
            'trigger contextchanged .contextsensitiv http://tld.com/groups/group1',
            'trigger contextchanged #content http://tld.com/groups/group1',
        ]);
    });

    QUnit.test('constructor', (assert) => {
        const listing = new PrincipalListing();
        assert.true(listing.actions instanceof PrincipalActions);
    });

    QUnit.test('noop', (assert) => {
        const listing = new PrincipalListing();
        const evt = $.Event('click');
        listing.noop(evt);
        assert.true(evt.isDefaultPrevented());
    });

    QUnit.test('set_selected and reset_selected', function (assert) {
        const left = create_left_column(this.container);
        const items = $('ul.leftlisting li', left);
        const listing = new PrincipalListing();

        listing.set_selected(items.first());
        assert.true(items.first().hasClass('selected'));
        assert.false(items.last().hasClass('selected'));

        listing.reset_selected($('ul.leftlisting', left));
        assert.strictEqual($('li.selected', left).length, 0);
    });
});

QUnit.module('cone.ugm.listing.LeftPrincipalListing', (hooks) => {
    setup_listing_hooks(hooks);

    QUnit.test('add_principal', function (assert) {
        const left = create_left_column(this.container);
        new LeftPrincipalListing(this.container);

        const evt = $.Event('click');
        $('div.add_button button', left).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(evt.isPropagationStopped());
        assert.strictEqual($('li.selected', left).length, 0);
        assert.verifySteps([
            'action add .right_column inner http://tld.com/users',
            'params {"type":"user"}',
        ]);
    });

    QUnit.test('delete actions', function (assert) {
        const left = create_left_column(this.container);
        new LeftPrincipalListing(this.container);

        $('a.delete_item', left).trigger('click');
        assert.verifySteps(['dialog Delete Principal']);

        // check disabled action isolated from item navigation
        $('ul.leftlisting li', left).off('click');
        const evt = $.Event('click');
        $('a.delete_item_disabled', left).trigger(evt);
        assert.true(evt.isDefaultPrevented());
        assert.verifySteps([]);
    });

    QUnit.test('show_item', function (assert) {
        const left = create_left_column(this.container);
        new LeftPrincipalListing(this.container);
        const items = $('ul.leftlisting li', left);

        const evt = $.Event('click');
        items.first().trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(items.first().hasClass('selected'));
        assert.false(items.last().hasClass('selected'));
        assert.verifySteps([
            'action rightcolumn .right_column replace http://tld.com/users/user1',
            'params {"a":"1"}',
        ]);
    });
});

QUnit.module('cone.ugm.listing.RightPrincipalListing', (hooks) => {
    setup_listing_hooks(hooks);

    QUnit.test('add and remove actions', function (assert) {
        const right = create_right_column(this.container);
        new RightPrincipalListing(this.container);

        $('a.add_item', right).trigger('click');
        $('a.remove_item', right).trigger('click');
        assert.verifySteps([
            'request http://tld.com/groups/group1/add_item',
            'request http://tld.com/groups/group2/remove_item',
        ]);

        // check disabled actions isolated from item navigation
        $('ul.rightlisting li', right).off('click');
        const add_evt = $.Event('click');
        $('a.add_item_disabled', right).trigger(add_evt);
        const remove_evt = $.Event('click');
        $('a.remove_item_disabled', right).trigger(remove_evt);
        assert.true(add_evt.isDefaultPrevented());
        assert.true(remove_evt.isDefaultPrevented());
        assert.verifySteps([]);
    });

    QUnit.test('show_item', function (assert) {
        const right = create_right_column(this.container);
        new RightPrincipalListing(this.container);
        const items = $('ul.rightlisting li', right);

        const evt = $.Event('click');
        items.first().trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(items.first().hasClass('selected'));
        assert.false(items.last().hasClass('selected'));
        assert.verifySteps([
            'trigger contextchanged .contextsensitiv http://tld.com/groups/group1',
            'trigger contextchanged #content http://tld.com/groups/group1',
        ]);
    });

    QUnit.test('list_related', function (assert) {
        const right = create_right_column(this.container);
        const listing = new RightPrincipalListing(this.container);
        const list_all = $('input.list_all', right);

        list_all.prop('checked', true);
        listing.list_related({ currentTarget: list_all[0] });
        list_all.prop('checked', false);
        listing.list_related({ currentTarget: list_all[0] });

        assert.verifySteps([
            'action allcolumnlisting div.right_column .columnlisting replace ' +
                'http://tld.com/users/user1',
            'params {"b":"2"}',
            'action columnlisting div.right_column .columnlisting replace ' +
                'http://tld.com/users/user1',
            'params {"b":"2"}',
        ]);
    });

    QUnit.test('list all action is bound', function (assert) {
        const right = create_right_column(this.container);
        new RightPrincipalListing(this.container);
        const list_all = $('input.list_all', right);

        list_all.trigger('click');

        assert.true(list_all.prop('checked'));
        assert.verifySteps([
            'action allcolumnlisting div.right_column .columnlisting replace ' +
                'http://tld.com/users/user1',
            'params {"b":"2"}',
        ]);
    });
});
