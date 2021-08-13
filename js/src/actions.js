import $ from 'jquery';
import ts from 'treibstoff';

class PrincipalActions {

    // delete item from database
    delete_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var elem = $(evt.currentTarget);
        var col = $('.cols .sort_col_1', elem.parent().parent());
        var id = col.text();
        id = id.replace('<', '&lt;');
        id = id.replace('>', '&gt;');
        var msg = 'Do you really want to delete this item?\n\n\n"' + id + '"';
        var options = {
            message: msg,
            action_id: 'delete_item'
        };
        var target = elem.attr('ajax:target');
        $.extend(options, bdajax.parsetarget(target));
        $.extend(options, {
            success: function(data) {
                if (!data) {
                    bdajax.error('Empty response');
                    return;
                }
                if (!data.success) {
                    bdajax.error(data.message);
                    return;
                }
                var li = elem.parent().parent();
                if (li.hasClass('selected')) {
                    var col = $('div.right_column');
                    col.empty();
                }
                li.remove();
            }
        });
        bdajax.dialog(options, function(options) {
            ugm.actions.perform(options);
        });
    }

    // add item as member in listing
    listing_add_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var elem = $(evt.currentTarget);
        var target = elem.attr('ajax:target');
        var options = bdajax.parsetarget(target);
        $.extend(options, {
            action_id: 'add_item',
            success: function(data) {
                if (!data) {
                    bdajax.error('Empty response');
                    return;
                }
                if (!data.success) {
                    bdajax.error(data.message);
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
                    .on('click', ugm.actions.listing_remove_item);
            }
        });
        ugm.actions.perform(options);
    }

    // remove item from member in listing
    listing_remove_item(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var elem = $(evt.currentTarget);
        var target = elem.attr('ajax:target');
        var options = bdajax.parsetarget(target);
        $.extend(options, {
            action_id: 'remove_item',
            success: function(data) {
                if (!data) {
                    bdajax.error('Empty response');
                    return;
                }
                if (!data.success) {
                    bdajax.error(data.message);
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
                    .on('click', ugm.actions.listing_add_item);
            }
        });
        ugm.actions.perform(options);
    }

    // perform listing item action
    perform(config) {
        bdajax.request({
            url: bdajax.parseurl(config.url) + '/' + config.action_id,
            type: 'json',
            params: config.params,
            success: config.success
        });
    }
}
