import $ from 'jquery';
import ts from 'treibstoff';

export class PrincipalActions {

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
        let options = {
            action_id: 'delete_item'
        };
        let target = elem.attr('ajax:target');
        $.extend(options, ts.parse_target(target));
        $.extend(options, {
            success: function(data) {
                if (!data) {
                    ts.show_error('Empty response');
                    return;
                }
                if (!data.success) {
                    ts.show_error(data.message);
                    return;
                }
                let li = elem.parent().parent();
                if (li.hasClass('selected')) {
                    let col = $('div.right_column');
                    col.empty();
                }
                li.remove();
            }
        });
        let msg = `Do you really want to delete this item?\n\n\n"${id}"`;
        ts.show_dialog({
            title: 'Delete Principal',
            message: msg,
            on_confirm: function(inst) {
                this.perform(options);
            }.bind(this)
        });
    }

    add_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        let elem = $(evt.currentTarget),
            target = elem.attr('ajax:target'),
            options = ts.parse_target(target),
            that = this;
        $.extend(options, {
            action_id: 'add_item',
            success: function(data) {
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
                    .on('click', function(e) {
                        e.preventDefault();
                    });
                $('.remove_item_disabled', elem.parent())
                    .off()
                    .removeClass('remove_item_disabled')
                    .addClass('remove_item')
                    .on('click', that.remove_item_handle);
            }
        });
        this.perform(options);
    }

    remove_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        let elem = $(evt.currentTarget),
            target = elem.attr('ajax:target'),
            options = ts.parse_target(target),
            that = this;
        $.extend(options, {
            action_id: 'remove_item',
            success: function(data) {
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
                    .on('click', function(e) {
                        e.preventDefault();
                    });
                $('.add_item_disabled', elem.parent())
                    .off()
                    .removeClass('add_item_disabled')
                    .addClass('add_item')
                    .on('click', that.add_item_handle);
            }
        });
        this.perform(options);
    }

    perform(opts) {
        ts.ajax.request({
            url: `${ts.parse_url(opts.url)}/${opts.action_id}`,
            type: 'json',
            params: opts.params,
            success: opts.success
        });
    }
}
