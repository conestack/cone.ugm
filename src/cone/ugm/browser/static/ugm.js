/* 
 * ugm JS
 * 
 * Requires: bdajax
 */

(function($) {

    $(document).ready(function() {
        bdajax.register(ugm.add_principal_button_binder.bind(ugm), true);
        bdajax.register(ugm.left_listing_nav_binder.bind(ugm), true);
        bdajax.register(ugm.right_listing_nav_binder.bind(ugm), true);
        bdajax.register(ugm.listing_filter_binder.bind(ugm), true);
        bdajax.register(ugm.listing_actions_binder.bind(ugm), true);
        bdajax.register(ugm.listing_related_binder.bind(ugm), true);
    });

    ugm = {

        // localmanager
        localmanager: {
            autocomplete_gid: function(request, callback) {
                bdajax.request({
                    success: function(data) {
                        callback(data);
                    },
                    url: 'group_id_vocab',
                    params: { term: request.term },
                    type: 'json'
                });
            }
        },

        // bind add principal button
        add_principal_button_binder: function(context) {
            $('div.add_button button', context).on('click', function() {
                $('.left_column ul.leftlisting li').removeClass('selected');
            });
        },

        // bind left listing trigger
        left_listing_nav_binder: function(context) {
            $('ul.leftlisting li', context)
                .off()
                .on('click', ugm.left_listing_nav_cb);
        },

        // left listing trigger callback
        left_listing_nav_cb: function(event) {
            var li = $(this);
            ugm.reset_listing_selected(li);

            // perform action manually
            var target = bdajax.parsetarget(li.attr('ajax:target'));
            bdajax.action({
                name: 'rightcolumn',
                selector: '.right_column',
                mode: 'replace',
                url: target.url,
                params: target.params
            });
            return false;
        },

        // bind right listing trigger
        right_listing_nav_binder: function(context) {
            $('ul.rightlisting li', context)
                .off()
                .on('click', ugm.right_listing_nav_cb);
        },

        // right listing trigger callback
        right_listing_nav_cb: function(event) {
            var li = $(this);
            ugm.reset_listing_selected(li);

            // reload context sensitiv tiles and context with new target
            var target = li.attr('ajax:target');
            bdajax.trigger('contextchanged', '.contextsensitiv', target);
            bdajax.trigger('contextchanged', '#content', target);
            return false;
        },

        // bind listing item actions
        listing_actions_binder: function(context) {

            // bind delete actions
            $('div.columnitems div.actions a.delete_item', context)
                .off()
                .on('click', ugm.actions.delete_item);

            // bind disabled delete actions
            $('div.columnitems div.actions a.delete_item_disabled', context)
                .off()
                .on('click', function(event) {
                    event.preventDefault();
                });

            // bind add actions
            $('div.columnitems div.actions a.add_item', context)
                .off()
                .on('click', ugm.actions.listing_add_item);

            // bind disabled add actions
            $('div.columnitems div.actions a.add_item_disabled', context)
                .off()
                .on('click', function(event) {
                    event.preventDefault();
                });

            // bind remove actions
            $('div.columnitems div.actions a.remove_item', context)
                .off()
                .on('click', ugm.actions.listing_remove_item);

            // bind disabled remove actions
            $('div.columnitems div.actions a.remove_item_disabled', context)
                .off()
                .on('click', function(event) {
                    event.preventDefault();
                });
        },

        // object containing ugm action callbacks
        actions: {

            // delete item from database
            delete_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elem = $(event.currentTarget);
                var col = $('.cols .sort_col_1', elem.parent().parent());
                var id = col.text();
                id = id.replace('<', '&lt;');
                id = id.replace('>', '&gt;');
                var msg = 'Do you really want to delete this item?\n\n\n"' + 
                          id + '"';
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
            },

            // add item as member in listing
            listing_add_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elem = $(event.currentTarget);
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
                            .on('click', function(event) {
                                event.preventDefault();
                            });
                        $('.remove_item_disabled', elem.parent())
                            .off()
                            .removeClass('remove_item_disabled')
                            .addClass('remove_item')
                            .on('click', ugm.actions.listing_remove_item);
                    }
                });
                ugm.actions.perform(options);
            },

            // remove item from member in listing
            listing_remove_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elem = $(event.currentTarget);
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
                            .on('click', function(event) {
                                event.preventDefault();
                            });
                        $('.add_item_disabled', elem.parent())
                            .off()
                            .removeClass('add_item_disabled')
                            .addClass('add_item')
                            .on('click', ugm.actions.listing_add_item);
                    }
                });
                ugm.actions.perform(options);
            },

            // perform listing item action
            perform: function(config) {
                bdajax.request({
                    url: bdajax.parseurl(config.url) + '/' + config.action_id,
                    type: 'json',
                    params: config.params,
                    success: config.success
                });
            }
        },

        // bind listing filter
        listing_filter_binder: function(context) {
            var filter_selector = 'div.column_filter input';
            var filter_name = 'filter';
            cone.batcheditems_filter_binder(
                context,
                filter_selector,
                filter_name
            );
        },

        // reset selcted item in listing
        reset_listing_selected: function(li) {
            $('li', li.parent()).removeClass('selected');
            li.addClass('selected');
        },

        // bind related items filter
        // XXX: changed to list_all, wait for group in group to fix naming
        listing_related_binder: function(context) {
            $('div.column_limit input.list_all', context)
                .off()
                .on('click', ugm.listing_related_cb);
        },

        // callback when related filter gets toggled
        listing_related_cb: function(event) {
            var elem = $(this);
            var action;
            if (elem.prop('checked')) {
                action = 'allcolumnlisting';
            } else {
                action = 'columnlisting';
            }
            var target = bdajax.parsetarget(elem.attr('ajax:target'));
            bdajax.action({
                name: action,
                selector: 'div.right_column .columnlisting',
                mode: 'replace',
                url: target.url,
                params: target.params
            });
        }
    };

})(jQuery);
