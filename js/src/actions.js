import $ from 'jquery';
import ts from 'treibstoff';

function escape_html(value) {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

export class PrincipalActions {
    constructor() {
        this.delete_item = this.delete_item.bind(this);
        this.add_item = this.add_item.bind(this);
        this.remove_item = this.remove_item.bind(this);
    }

    delete_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        const elem = $(evt.currentTarget),
            col = $('.cols .sort_col_1', elem.parent().parent()),
            id = escape_html(col.text());
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
        const msg = `Do you really want to delete this item?<br><br>"${id}"`;
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
                    .on('click', this.remove_item);
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
                    .on('click', this.add_item);
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
