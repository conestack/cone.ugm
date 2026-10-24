var cone_ugm = (function (exports, $, ts, cone) {
    'use strict';

    class PrincipalActions {
        constructor() {
            this.delete_item = this.delete_item.bind(this);
            this.add_item = this.add_item.bind(this);
            this.remove_item = this.remove_item.bind(this);
        }
        delete_item(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            let elem = $(evt.currentTarget),
                col = $('.cols .sort_col_1', elem.parent().parent()),
                id = col.text();
            id = id.replace('<', '&lt;');
            id = id.replace('>', '&gt;');
            const options = {
                action_id: 'delete_item',
            };
            const target = elem.attr('ajax:target');
            $.extend(options, ts.ajax.parse_target(target));
            $.extend(options, {
                success: (data) => {
                    if (!data) {
                        ts.show_error('Empty response');
                        return;
                    }
                    if (!data.success) {
                        ts.show_error(data.message);
                        return;
                    }
                    const li = elem.parent().parent();
                    if (li.hasClass('selected')) {
                        const col = $('div.right_column');
                        col.empty();
                    }
                    li.remove();
                },
            });
            const msg = `Do you really want to delete this item?\n\n\n"${id}"`;
            ts.show_dialog({
                title: 'Delete Principal',
                message: msg,
                on_confirm: function (_inst) {
                    this.perform(options);
                }.bind(this),
            });
        }
        add_item(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            const elem = $(evt.currentTarget),
                target = elem.attr('ajax:target'),
                options = ts.ajax.parse_target(target);
            $.extend(options, {
                action_id: 'add_item',
                success: (data) => {
                    if (!data) {
                        ts.show_error('Empty response');
                        return;
                    }
                    if (!data.success) {
                        ts.show_error(data.message);
                        return;
                    }
                    elem.off()
                        .removeClass('add_item')
                        .addClass('add_item_disabled')
                        .on('click', (e) => {
                            e.preventDefault();
                        });
                    $('.remove_item_disabled', elem.parent())
                        .off()
                        .removeClass('remove_item_disabled')
                        .addClass('remove_item')
                        .on('click', this.remove_item_handle);
                },
            });
            this.perform(options);
        }
        remove_item(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            const elem = $(evt.currentTarget),
                target = elem.attr('ajax:target'),
                options = ts.ajax.parse_target(target);
            $.extend(options, {
                action_id: 'remove_item',
                success: (data) => {
                    if (!data) {
                        ts.show_error('Empty response');
                        return;
                    }
                    if (!data.success) {
                        ts.show_error(data.message);
                        return;
                    }
                    elem.off()
                        .removeClass('remove_item')
                        .addClass('remove_item_disabled')
                        .on('click', (e) => {
                            e.preventDefault();
                        });
                    $('.add_item_disabled', elem.parent())
                        .off()
                        .removeClass('add_item_disabled')
                        .addClass('add_item')
                        .on('click', this.add_item_handle);
                },
            });
            this.perform(options);
        }
        perform(opts) {
            ts.ajax.request({
                url: `${ts.parse_url(opts.url)}/${opts.action_id}`,
                type: 'json',
                params: opts.params,
                success: opts.success,
            });
        }
    }

    class PrincipalListing {
        static initialize(context) {
            cone.BatchedItemsSearch.initialize(context, 'div.column_filter input', 'filter');
            new LeftPrincipalListing(context);
            new RightPrincipalListing(context);
        }
        constructor() {
            this.actions = new PrincipalActions();
        }
        noop(evt) {
            evt.preventDefault();
        }
        set_selected(item) {
            this.reset_selected(item.parent());
            item.addClass('selected');
        }
        reset_selected(listing) {
            $('li', listing).removeClass('selected');
        }
    }
    class LeftPrincipalListing extends PrincipalListing {
        constructor(context) {
            super();
            const add_btn = $('div.add_button button', context);
            add_btn.off('click').on('click', this.add_principal.bind(this));
            const actions = $('div.columnitems div.actions', context);
            const delete_actions = $('a.delete_item', actions);
            delete_actions.off().on('click', this.actions.delete_item);
            const delete_actions_disabled = $('a.delete_item_disabled', actions);
            delete_actions_disabled.off().on('click', this.noop);
            const listing_items = $('ul.leftlisting li', context);
            listing_items.off().on('click', this.show_item.bind(this));
        }
        add_principal(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            const listing = $('.left_column ul.leftlisting');
            this.reset_selected(listing);
            const elem = $(evt.currentTarget),
                target = ts.ajax.parse_target(elem.attr('ajax:target'));
            ts.ajax.action({
                name: 'add',
                selector: '.right_column',
                mode: 'inner',
                url: target.url,
                params: target.params,
            });
        }
        show_item(evt) {
            const li = $(evt.currentTarget);
            this.set_selected(li);
            const target = ts.ajax.parse_target(li.attr('ajax:target'));
            ts.ajax.action({
                name: 'rightcolumn',
                selector: '.right_column',
                mode: 'replace',
                url: target.url,
                params: target.params,
            });
            return false;
        }
    }
    class RightPrincipalListing extends PrincipalListing {
        constructor(context) {
            super();
            const actions = $('div.columnitems div.actions', context);
            const add_actions = $('a.add_item', actions);
            add_actions.off().on('click', this.actions.add_item);
            const add_actions_disabled = $('a.add_item_disabled', actions);
            add_actions_disabled.off().on('click', this.noop);
            const remove_actions = $('a.remove_item', actions);
            remove_actions.off().on('click', this.actions.remove_item);
            const remove_actions_disabled = $('a.remove_item_disabled', actions);
            remove_actions_disabled.off().on('click', this.noop);
            const listing_items = $('ul.rightlisting li', context);
            listing_items.off().on('click', this.show_item.bind(this));
            const list_all_action = $('div.column_limit input.list_all', context);
            list_all_action.off().on('click', this.list_related.bind(this));
        }
        show_item(evt) {
            const li = $(evt.currentTarget);
            this.set_selected(li);
            const target = li.attr('ajax:target');
            ts.ajax.trigger('contextchanged', '.contextsensitiv', target);
            ts.ajax.trigger('contextchanged', '#content', target);
            return false;
        }
        list_related(evt) {
            let elem = $(evt.currentTarget),
                action;
            if (elem.prop('checked')) {
                action = 'allcolumnlisting';
            } else {
                action = 'columnlisting';
            }
            const target = ts.ajax.parse_target(elem.attr('ajax:target'));
            ts.ajax.action({
                name: action,
                selector: 'div.right_column .columnlisting',
                mode: 'replace',
                url: target.url,
                params: target.params,
            });
        }
    }

    $(() => {
        ts.ajax.register(PrincipalListing.initialize, true);
    });

    exports.LeftPrincipalListing = LeftPrincipalListing;
    exports.PrincipalActions = PrincipalActions;
    exports.PrincipalListing = PrincipalListing;
    exports.RightPrincipalListing = RightPrincipalListing;

    Object.defineProperty(exports, '__esModule', { value: true });


    window.ugm = exports;


    return exports;

})({}, jQuery, treibstoff, cone);
