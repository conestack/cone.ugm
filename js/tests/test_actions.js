import $ from 'jquery';
import ts from 'treibstoff';
import { PrincipalActions } from '../src/actions.js';

QUnit.module('cone.ugm.actions.PrincipalActions', (hooks) => {
    let container, original_ts;

    hooks.beforeEach(() => {
        container = $('<div />').appendTo('body');
        original_ts = {
            request: ts.ajax.request,
            show_dialog: ts.show_dialog,
            show_error: ts.show_error,
        };
        ts.show_error = (message) => {
            QUnit.config.current.assert.step(`error: ${message}`);
        };
    });

    hooks.afterEach(() => {
        ts.ajax.request = original_ts.request;
        ts.show_dialog = original_ts.show_dialog;
        ts.show_error = original_ts.show_error;
        container.remove();
    });

    function create_delete_listing() {
        $(`
            <div class="right_column"><span>principal</span></div>
            <ul class="leftlisting">
              <li>
                <div class="cols"><div class="sort_col_1">user&lt;1&gt;</div></div>
                <div class="actions">
                  <a class="delete_item" ajax:target="http://tld.com/users/user1?a=b">x</a>
                </div>
              </li>
            </ul>
        `).appendTo(container);
        const actions = new PrincipalActions();
        $('a.delete_item', container).on('click', actions.delete_item);
    }

    function create_item_actions(css) {
        $(`
            <div class="actions">
              <a class="${css}" ajax:target="http://tld.com/groups/group1?id=user1">+</a>
              <a class="add_item_disabled" ajax:target="http://tld.com/groups/group1?id=user1">+</a>
              <a class="remove_item_disabled" ajax:target="http://tld.com/groups/group1?id=user1">-</a>
            </div>
        `).appendTo(container);
        const actions = new PrincipalActions();
        $('a.add_item', container).on('click', actions.add_item);
        $('a.remove_item', container).on('click', actions.remove_item);
    }

    QUnit.test('delete_item asks for confirmation and performs request', (assert) => {
        create_delete_listing();
        let dialog_opts, request_opts;
        ts.show_dialog = (opts) => {
            dialog_opts = opts;
        };
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };

        const evt = $.Event('click');
        $('a.delete_item', container).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(evt.isPropagationStopped());
        assert.strictEqual(dialog_opts.title, 'Delete Principal');
        assert.strictEqual(
            dialog_opts.message,
            'Do you really want to delete this item?<br><br>"user&lt;1&gt;"',
        );
        assert.strictEqual(request_opts, undefined);

        dialog_opts.on_confirm();

        assert.strictEqual(request_opts.url, 'http://tld.com/users/user1/delete_item');
        assert.strictEqual(request_opts.type, 'json');
        assert.deepEqual(request_opts.params, { a: 'b' });
    });

    QUnit.test('delete_item displays principal id as text in dialog', (assert) => {
        create_delete_listing();
        const id = `a<b>c<img class="injected">&amp;"'`;
        $('.sort_col_1', container).text(id);

        $('a.delete_item', container).trigger('click');

        const body = $('.modal.dialog .modal-body');
        assert.strictEqual($('b, img', body).length, 0);
        assert.strictEqual(body.text(), `Do you really want to delete this item?"${id}"`);
        $('.modal.dialog button.cancel').trigger('click');
        assert.strictEqual($('.modal.dialog').length, 0);
    });

    QUnit.test('delete_item shows principal id on its own line in dialog', (assert) => {
        create_delete_listing();

        $('a.delete_item', container).trigger('click');

        const body = $('.modal.dialog .modal-body');
        const lines = body
            .contents()
            .toArray()
            .map((node) => (node.nodeName === 'BR' ? '<br>' : node.textContent));
        assert.deepEqual(lines, [
            'Do you really want to delete this item?',
            '<br>',
            '<br>',
            '"user<1>"',
        ]);
        $('.modal.dialog button.cancel').trigger('click');
    });

    QUnit.test('delete_item failure', (assert) => {
        create_delete_listing();
        let request_opts;
        ts.show_dialog = (opts) => {
            opts.on_confirm();
        };
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };
        $('a.delete_item', container).trigger('click');

        request_opts.success(null);
        request_opts.success({ success: false, message: 'Deletion failed' });

        assert.verifySteps(['error: Empty response', 'error: Deletion failed']);
        assert.strictEqual($('ul.leftlisting li', container).length, 1);
    });

    QUnit.test('delete_item removes item', (assert) => {
        create_delete_listing();
        let request_opts;
        ts.show_dialog = (opts) => {
            opts.on_confirm();
        };
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };
        $('a.delete_item', container).trigger('click');

        request_opts.success({ success: true });

        assert.strictEqual($('ul.leftlisting li', container).length, 0);
        assert.strictEqual($('div.right_column', container).html(), '<span>principal</span>');
    });

    QUnit.test('delete_item removes selected item and empties right column', (assert) => {
        create_delete_listing();
        $('ul.leftlisting li', container).addClass('selected');
        let request_opts;
        ts.show_dialog = (opts) => {
            opts.on_confirm();
        };
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };
        $('a.delete_item', container).trigger('click');

        request_opts.success({ success: true });

        assert.strictEqual($('ul.leftlisting li', container).length, 0);
        assert.strictEqual($('div.right_column', container).html(), '');
    });

    QUnit.test('add_item performs request', (assert) => {
        create_item_actions('add_item');
        let request_opts;
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };

        const evt = $.Event('click');
        $('a.add_item', container).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(evt.isPropagationStopped());
        assert.strictEqual(request_opts.url, 'http://tld.com/groups/group1/add_item');
        assert.strictEqual(request_opts.type, 'json');
        assert.deepEqual(request_opts.params, { id: 'user1' });
    });

    QUnit.test('add_item failure', (assert) => {
        create_item_actions('add_item');
        let request_opts;
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };
        $('a.add_item', container).trigger('click');

        request_opts.success(null);
        request_opts.success({ success: false, message: 'Adding failed' });

        assert.verifySteps(['error: Empty response', 'error: Adding failed']);
        assert.strictEqual($('a.add_item', container).length, 1);
    });

    QUnit.test('add_item disables add and enables remove action', (assert) => {
        create_item_actions('add_item');
        const requests = [];
        ts.ajax.request = (opts) => {
            requests.push(opts);
        };
        const add_action = $('a.add_item', container);
        add_action.trigger('click');

        requests[0].success({ success: true });

        assert.true(add_action.hasClass('add_item_disabled'));
        assert.false(add_action.hasClass('add_item'));
        assert.strictEqual($('a.remove_item', container).length, 1);
        assert.strictEqual($('a.remove_item_disabled', container).length, 0);

        // disabled add action only prevents default
        const evt = $.Event('click');
        add_action.trigger(evt);
        assert.true(evt.isDefaultPrevented());
        assert.strictEqual(requests.length, 1);
    });

    QUnit.test('remove action enabled by add_item performs request', (assert) => {
        create_item_actions('add_item');
        const requests = [];
        ts.ajax.request = (opts) => {
            requests.push(opts);
        };
        $('a.add_item', container).trigger('click');
        requests[0].success({ success: true });

        const evt = $.Event('click');
        $('a.remove_item', container).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.strictEqual(requests.length, 2);
        assert.strictEqual(requests[1].url, 'http://tld.com/groups/group1/remove_item');
        assert.deepEqual(requests[1].params, { id: 'user1' });
    });

    QUnit.test('remove_item performs request', (assert) => {
        create_item_actions('remove_item');
        let request_opts;
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };

        const evt = $.Event('click');
        $('a.remove_item', container).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.true(evt.isPropagationStopped());
        assert.strictEqual(request_opts.url, 'http://tld.com/groups/group1/remove_item');
        assert.strictEqual(request_opts.type, 'json');
        assert.deepEqual(request_opts.params, { id: 'user1' });
    });

    QUnit.test('remove_item failure', (assert) => {
        create_item_actions('remove_item');
        let request_opts;
        ts.ajax.request = (opts) => {
            request_opts = opts;
        };
        $('a.remove_item', container).trigger('click');

        request_opts.success(null);
        request_opts.success({ success: false, message: 'Removing failed' });

        assert.verifySteps(['error: Empty response', 'error: Removing failed']);
        assert.strictEqual($('a.remove_item', container).length, 1);
    });

    QUnit.test('remove_item disables remove and enables add action', (assert) => {
        create_item_actions('remove_item');
        const requests = [];
        ts.ajax.request = (opts) => {
            requests.push(opts);
        };
        const remove_action = $('a.remove_item', container);
        remove_action.trigger('click');

        requests[0].success({ success: true });

        assert.true(remove_action.hasClass('remove_item_disabled'));
        assert.false(remove_action.hasClass('remove_item'));
        assert.strictEqual($('a.add_item', container).length, 1);
        assert.strictEqual($('a.add_item_disabled', container).length, 0);

        // disabled remove action only prevents default
        const evt = $.Event('click');
        remove_action.trigger(evt);
        assert.true(evt.isDefaultPrevented());
        assert.strictEqual(requests.length, 1);
    });

    QUnit.test('add action enabled by remove_item performs request', (assert) => {
        create_item_actions('remove_item');
        const requests = [];
        ts.ajax.request = (opts) => {
            requests.push(opts);
        };
        $('a.remove_item', container).trigger('click');
        requests[0].success({ success: true });

        const evt = $.Event('click');
        $('a.add_item', container).trigger(evt);

        assert.true(evt.isDefaultPrevented());
        assert.strictEqual(requests.length, 2);
        assert.strictEqual(requests[1].url, 'http://tld.com/groups/group1/add_item');
        assert.deepEqual(requests[1].params, { id: 'user1' });
    });
});
