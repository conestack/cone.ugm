/* 
 * ugm JS
 * 
 * Requires: bdajax
 */

(function($) {

    $(document).ready(function() {
        ugm.key_binder();
        ugm.scroll_listings_to_selected();

        bdajax.register(ugm.add_principal_button_binder.bind(ugm), true);
        bdajax.register(ugm.left_listing_nav_binder.bind(ugm), true);
        bdajax.register(ugm.right_listing_nav_binder.bind(ugm), true);
        bdajax.register(ugm.listing_filter_binder.bind(ugm), true);
        bdajax.register(ugm.listing_sort_binder.bind(ugm), true);
        bdajax.register(ugm.listing_actions_binder.bind(ugm), true);
        bdajax.register(ugm.listing_related_binder.bind(ugm), true);
        bdajax.register(ugm.inout_actions_binder.bind(ugm), true);
        bdajax.register(ugm.inout_filter_binder.bind(ugm), true);
        bdajax.register(ugm.inout_select_binder.bind(ugm), true);
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

        // object to store global flags
        flags: {},

        // keyboard control keys status
        keys: {},

        // keydown / keyup binder for shift and ctrl keys
        key_binder: function() {
            $(document).bind('keydown', function(event) {
                switch (event.keyCode || event.which) {
                    case 16:
                        ugm.keys.shift_down = true;
                        break;
                    case 17:
                        ugm.keys.ctrl_down = true;
                        break;
                }
            });
            $(document).bind('keyup', function(event) {
                switch (event.keyCode || event.which) {
                    case 16:
                        ugm.keys.shift_down = false;
                           break;
                    case 17:
                        ugm.keys.ctrl_down = false;
                        break;
                }
            });
        },

        // bind add principal button
        add_principal_button_binder: function(context) {
            $('div.add_button button', context).bind('click', function() {
                $('.left_column ul.leftlisting li').removeClass('selected');
            });
        },

        // bind left listing trigger
        left_listing_nav_binder: function(context) {
            $('ul.leftlisting li', context)
                .unbind()
                .bind('click', ugm.left_listing_nav_cb);
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
                .unbind()
                .bind('click', ugm.right_listing_nav_cb);
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
                .unbind()
                .bind('click', ugm.actions.delete_item);

            // bind disabled delete actions
            $('div.columnitems div.actions a.delete_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });

            // bind add actions
            $('div.columnitems div.actions a.add_item', context)
                .unbind()
                .bind('click', ugm.actions.listing_add_item);

            // bind disabled add actions
            $('div.columnitems div.actions a.add_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });

            // bind remove actions
            $('div.columnitems div.actions a.remove_item', context)
                .unbind()
                .bind('click', ugm.actions.listing_remove_item);

            // bind disabled remove actions
            $('div.columnitems div.actions a.remove_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });
        },

        // bind inout item selection
        inout_select_binder: function(context) {
            $('div.inoutlisting div.li_trigger', context)
                .unbind()
                .bind('click', ugm.actions.inout_select_item);
        },

        // bind inout item actions
        inout_actions_binder: function(context) {

            // bind add actions
            $('div.inoutlisting div.actions a.add_item', context)
                .unbind()
                .bind('click', ugm.actions.inout_add_item);

            // bind remove actions
            $('div.inoutlisting div.actions a.remove_item', context)
                .unbind()
                .bind('click', ugm.actions.inout_remove_item);

            // bind button add action
            $('div.inoutlisting button.inout_add_item', context)
                .unbind()
                .bind('click', ugm.actions.inout_button_add_item);

            // bind button remove action
            $('div.inoutlisting button.inout_remove_item', context)
                .unbind()
                .bind('click', ugm.actions.inout_button_remove_item);
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
                        elem.unbind()
                            .removeClass('add_item')
                            .addClass('add_item_disabled')
                            .bind('click', function(event) {
                                event.preventDefault();
                            });
                        $('.remove_item_disabled', elem.parent())
                            .unbind()
                            .removeClass('remove_item_disabled')
                            .addClass('remove_item')
                            .bind('click', ugm.actions.listing_remove_item);
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
                        elem.unbind()
                            .removeClass('remove_item')
                            .addClass('remove_item_disabled')
                            .bind('click', function(event) {
                                event.preventDefault();
                            });
                        $('.add_item_disabled', elem.parent())
                            .unbind()
                            .removeClass('add_item_disabled')
                            .addClass('add_item')
                            .bind('click', ugm.actions.listing_add_item);
                    }
                });
                ugm.actions.perform(options);
            },

            // select item in inout widget
            inout_select_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elem = $(event.currentTarget);
                var li = elem.parent();
                if (!ugm.keys.ctrl_down && !ugm.keys.shift_down) {
                    $('li', li.parent().parent()).removeClass('selected');
                    li.addClass('selected');
                } else {
                    if (ugm.keys.ctrl_down) {
                        li.toggleClass('selected');
                    }
                    if (ugm.keys.shift_down) {
                        var listing = li.parent();
                        var selected = $('li.selected', listing);
                        // get nearest next selected item, disable others
                        var current_index = li.index();
                        // -1 means no other selected item
                        var nearest = -1;
                        var selected_index, selected_elem;
                        $(selected).each(function() {
                            selected_elem = $(this);
                            selected_index = selected_elem.index();
                            if (nearest == -1) {
                                nearest = selected_index;
                            } else if (current_index > selected_index) {
                                if (ugm.flags.select_direction > 0) {
                                    if (selected_index < nearest) {
                                        nearest = selected_index;
                                    }
                                } else {
                                    if (selected_index > nearest) {
                                        nearest = selected_index;
                                    }
                                }
                            } else if (current_index < selected_index) {
                                if (selected_index < nearest) {
                                    nearest = selected_index;
                                }
                            }
                        });
                        if (nearest == -1) {
                            li.addClass('selected');
                        } else {
                            $('li', listing).removeClass('selected');
                            var start, end;
                            if (current_index < nearest) {
                                ugm.flags.select_direction = -1;
                                start = current_index;
                                end = nearest;
                            } else {
                                ugm.flags.select_direction = 1;
                                start = nearest;
                                end = current_index;
                            }
                            $('li', listing)
                                .slice(start, end + 1)
                                .addClass('selected');
                            
                        }
                    }
                    if (li.parent().hasClass('inoutleftlisting')) {
                        $('.inoutrightlisting li',
                          li.parent().parent()).removeClass('selected');
                    } else {
                        $('.inoutleftlisting li',
                          li.parent().parent()).removeClass('selected');
                    }
                }
            },

            // add item as member in inout widget via button
            inout_button_add_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elems = $('ul.inoutleftlisting li.selected');
                if (!elems.length) {
                    return;
                }
                // read selected item id's
                var items = ugm.inout_extract_selected(elems);
                // parse principal target from action link
                var target = $('a.add_item', elems).first().attr('ajax:target');
                var options = bdajax.parsetarget(target);
                // overwrite id param
                options.params['id'] = items;
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
                        $('.add_item', elems)
                            .removeClass('enabled')
                            .addClass('hidden');
                        $('.remove_item', elems)
                            .removeClass('hidden')
                            .addClass('enabled');
                        var new_container = $(
                            'ul.inoutrightlisting',
                            elems.first().parent().parent());
                        ugm.inout_move_item(elems, new_container);
                    }
                });
                ugm.actions.perform(options);
            },

            // remove item from member in inout widget via button
            inout_button_remove_item: function(event) {
                event.preventDefault();
                event.stopPropagation();
                var elems = $('ul.inoutrightlisting li.selected');
                if (!elems.length) {
                    return;
                }
                // read selected item id's
                var items = ugm.inout_extract_selected(elems);
                // parse principal target from action link
                var target = $('a.add_item', elems).first().attr('ajax:target');
                var options = bdajax.parsetarget(target);
                // overwrite id param
                options.params['id'] = items;
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
                        $('.remove_item', elems)
                            .removeClass('enabled')
                            .addClass('hidden');
                        $('.add_item', elems)
                            .removeClass('hidden')
                            .addClass('enabled');
                        var new_container = $(
                            'ul.inoutleftlisting',
                            elems.first().parent().parent());
                        ugm.inout_move_item(elems, new_container);
                    }
                });
                ugm.actions.perform(options);
            },

            // add item as member in inout widget
            inout_add_item: function(event) {
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
                        elem.removeClass('enabled')
                            .addClass('hidden');
                        $('.remove_item', elem.parent())
                            .removeClass('hidden')
                            .addClass('enabled');
                        var to_move = elem.parent().parent();
                        var new_container = $(
                            'ul.inoutrightlisting', to_move.parent().parent());
                        ugm.inout_move_item(to_move, new_container);
                    }
                });
                ugm.actions.perform(options);
            },

            // remove item from member in inout widget
            inout_remove_item: function(event) {
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
                        elem.removeClass('enabled')
                            .addClass('hidden');
                        $('.add_item', elem.parent())
                            .removeClass('hidden')
                            .addClass('enabled');
                        var to_move = elem.parent().parent();
                        var new_container = $(
                            'ul.inoutleftlisting', to_move.parent().parent());
                        ugm.inout_move_item(to_move, new_container);
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

        // bind filter
        filter_binder: function(context, input_selector, listing_selector) {

            // reset filter input field
            $(input_selector, context).bind('focus', function() {
                this.value = '';
                $(this).css('color', '#000');
            });

            // refresh related column with filtered listing
            $(input_selector, context).bind('keyup', function() {
                var current_filter = this.value.toLowerCase();
                $(listing_selector, $(this).parent().parent())
                    .each(function() {
                        var li = $(this);
                        var val = $('div.cols', li).html().toLowerCase();
                        if (val.indexOf(current_filter) != -1) {
                            li.removeClass('hidden');
                        } else {
                            li.addClass('hidden');    
                        }
                    });
            });
        },

        // bind listing filter
        listing_filter_binder: function(context) {
            var filter_selector = 'div.column_filter input';
            // reset filter input field
            $(filter_selector, context).bind('focus', function() {
                this.value = '';
                $(this).css('color', '#000');
            });
            var trigger_search = function(input) {
                var term = input.attr('value');
                cone.batcheditems_handle_filter(input, 'column_filter', term);
            };
            var searchfield = $(filter_selector, context);
            searchfield.unbind('keypress').bind('keypress', function(event) {
                if (event.keyCode == 13) {
                    event.preventDefault();
                }
            });
            searchfield.unbind('keyup').bind('keyup', function(event) {
                if (event.keyCode == 13) {
                    event.preventDefault();
                    trigger_search($(this));
                }
            });
            searchfield.unbind('change').bind('change', function(event) {
                event.preventDefault();
                trigger_search($(this));
            });
        },

        // bind inout filter
        inout_filter_binder: function(context) {

            // left listing
            ugm.filter_binder(context,
                              'div.left_column_filter input',
                              'ul.inoutleftlisting li');

            // right listing
            ugm.filter_binder(context,
                              'div.right_column_filter input',
                              'ul.inoutrightlisting li');
        },

        // reset selcted item in listing
        reset_listing_selected: function(li) {
            $('li', li.parent()).removeClass('selected');
            li.addClass('selected');
        },

        // bind related items filter - XXX: changed to list_all, wait
        // for group in group to fix naming
        listing_related_binder: function(context) {
            $('#list_all', context)
                .unbind()
                .bind('click', ugm.listing_related_cb);
        },

        // callback when related filter gets toggled
        listing_related_cb: function(event) {
            var elem = $(this);
            var action;
            if (elem.attr('checked')) {
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
        },

        // scroll column listings to selected items
        scroll_listings_to_selected: function() {
            ugm.listing_scroll_to_selected('.selected', $('ul.leftlisting'));
            ugm.listing_scroll_to_selected('.selected', $('ul.rightlisting'));
        },

        // scroll listing parent to element found by selector
        listing_scroll_to_selected: function(selector, listing) {
            var elem = $(selector, listing);
            if (elem.length) {
                var container = listing.parent();
                var listing_h = listing.height();
                var container_h = container.height();
                container.scrollTop(0);
                if (listing_h > container_h) {
                    var sel_y = elem.position().top - container_h;
                    var sel_h = elem.height();
                    if (sel_y > 0) {
                        container.scrollTop(sel_y + sel_h);
                    }
                }
            }
        },

        // scroll listing parent to element found by selector
        inout_scroll_to_selected: function(selector, container) {
            var elem = $(selector, container).first();
            if (elem.length) {
                container.scrollTop(0);
                var container_top = container.position().top;
                var container_height = container.height();
                var elem_top = elem.position().top;
                if (elem_top > container_top + container_height) {
                    var delta = elem_top - container_top;
                    container.scrollTop(delta);
                }
            }
        },

        // toggle inout widget item
        inout_move_item: function(elems, new_container) {
            var old_container = elems.first().parent();
            var to_move;
            $(elems).each(function() {
                to_move = $(this).detach();
                new_container.append(to_move);
            });
            $('li', new_container).sortElements(function(a, b) {
                var sel = 'div.sort_col_1';
                a = ugm.listing_sort_value(sel, a);
                b = ugm.listing_sort_value(sel, b);
                return naturalSort(a, b);
            });
            ugm.inout_scroll_to_selected(
                '.selected', new_container);
            $('li', elems.first().parent().parent()).removeClass('selected');
            elems.addClass('selected');
        },

        // inout listing extract selected ids
        inout_extract_selected: function(elems) {
            var items = new Array();
            var item;
            $(elems).each(function() {
                target = $(this).attr('ajax:target');
                item = target.substring(
                    target.lastIndexOf('/') + 1, target.length);
                items.push(item);
            });
            return items;
        },

        listing_sort_value: function(selector, context) {
            return $(selector, context).text();
        },

        // sort listings binder
        listing_sort_binder: function(context) {
            var sort_links = $('.columnsorting button', context);
            sort_links.unbind().bind('click', function(event) {
                bdajax.spinner.show();
                var elem = $(this);
                var inv = elem.hasClass('inv');
                var links = elem.parent().parent();
                $('button', links).removeClass('default')
                                  .removeClass('inv')
                                  .removeClass('asc')
                                  .removeClass('desc');
                var cont = $('.columnitems', elem.parent().parent().parent());
                if (inv) {
                    elem.addClass('asc');
                } else {
                    elem.addClass('inv').addClass('desc');
                }
                var sortname = elem.attr('id');
                if ($.browser.msie && ($.browser.version == 7)) {
                    sortname = sortname.substr(sortname.lastIndexOf('/') + 1);
                }
                var sel = '.' + sortname;
                $('li', cont).sortElements(function(a, b) {
                    a = ugm.listing_sort_value(sel, a);
                    b = ugm.listing_sort_value(sel, b);
                    if (inv) {
                        return naturalSort(b, a);
                    } else {
                        return naturalSort(a, b);
                    }
                });
                ugm.scroll_listings_to_selected();
                bdajax.spinner.hide();
            });
            $('.columnsorting button.default', context).trigger('click');
        }
    };

})(jQuery);
