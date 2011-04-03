/* 
 * ugm JS
 * 
 * Requires: bdajax
 */

(function($) {
    
    $(document).ready(function() {
        // initial binding
        ugm.left_listing_nav_binder();
        //ugm.right_listing_nav_binder();
        ugm.listing_filter_binder();
        ugm.listing_sort_binder();
        ugm.listing_actions_binder();
        ugm.listing_related_binder();
        ugm.scroll_listings_to_selected();
        
        // add after ajax binding to bdajax
        $.extend(bdajax.binders, {
            left_listing_nav_binder: ugm.left_listing_nav_binder,
            //right_listing_nav_binder: ugm.right_listing_nav_binder,
            listing_filter_binder: ugm.listing_filter_binder,
            listing_sort_binder: ugm.listing_sort_binder,
            listing_actions_binder: ugm.listing_actions_binder,
            listing_related_binder: ugm.listing_related_binder
        });
    });
    
    ugm = {
        
        // bind left listing trigger
        left_listing_nav_binder: function(context) {
            $('ul.leftlisting div.li_trigger', context)
                .unbind()
                .bind('click', ugm.left_listing_nav_cb);
        },
        
        // left listing trigger callback
        left_listing_nav_cb: function(event) {
            var li = $(this).parent();
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
            $('ul.rightlisting div.li_trigger', context)
                .unbind()
                .bind('click', ugm.right_listing_nav_cb);
        },
        
        // right listing trigger callback
        right_listing_nav_cb: function(event) {
            var li = $(this).parent();
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
            $('div.actions a.delete_item', context)
                .unbind()
                .bind('click', ugm.actions.delete_item);
            
            // bind disabled delete actions
            $('div.actions a.delete_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });
            
            // bind add actions
            $('div.actions a.add_item', context)
                .unbind()
                .bind('click', ugm.actions.add_item);
            
            // bind disabled add actions
            $('div.actions a.add_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });
            
            // bind remove actions
            $('div.actions a.remove_item', context)
                .unbind()
                .bind('click', ugm.actions.remove_item);
            
            // bind disabled remove actions
            $('div.actions a.remove_item_disabled', context)
                .unbind()
                .bind('click', function(event) {
                    event.preventDefault();
                });
        },
        
        // object containing ugm action callbacks
        actions: {
            
            // delete item from database
            delete_item: function(event) {
                event.preventDefault();
                var elem = $(event.currentTarget);
                var col = $('.head div.sort_col_3', elem.parent().parent());
                if (!col.length) {
                    col = $('.head .sort_col_1', elem.parent().parent());
                }
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
                            col.removeClass('box');
                            col.empty();
                        }
                        li.remove();
                    }
                });
                bdajax.dialog(options, function(options) {
                    ugm.actions.perform(options);
                });
            },
            
            // add item as member
            add_item: function(event) {
                event.preventDefault();
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
                            .bind('click', ugm.actions.remove_item);
                    }
                });
                ugm.actions.perform(options);
            },
            
            // remove item from member
            remove_item: function(event) {
                event.preventDefault();
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
                            .bind('click', ugm.actions.add_item);
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
            
            // reset filter input field
            $('div.column_filter input', context).bind('focus', function() {
                this.value = '';
                $(this).css('color', '#000');
            });
            
            // refresh focused column with filtered listing
            $('div.column_filter input', context).bind('keyup', function() {
                var current_filter = this.value.toLowerCase();
                $('div.columnitems li', $(this).parent().parent())
                    .each(function() {
                        var li = $(this);
                        var val = $('div.head', li).html().toLowerCase();
                        if (val.indexOf(current_filter) != -1) {
                            li.removeClass('hidden');
                        } else {
                            li.addClass('hidden');    
                        }
                    });
            });
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
            ugm.scroll_to_selected('.selected', $('ul.leftlisting'));
            ugm.scroll_to_selected('.selected', $('ul.rightlisting'));
        },
        
        // scroll listing parent to element found by selector
        scroll_to_selected: function(selector, listing) {
            var elem = $(selector, listing);
            if (elem.length) {
                var container = listing.parent();
                var listing_h = listing.height();
                var container_h = container.height();
                container.scrollTop(0);
                if (listing_h > container_h) {
                    var range_y = listing_h - container_h;
                    var sel_y = elem.position().top - container_h;
                    var sel_h = elem.height();
                    if (sel_y > 0) {
                        container.scrollTop(sel_y + sel_h);
                    }
                }
            }
        },
        
        // asc / desc sorting of listings
        listing_sort_func: function(name, inv) {
            var sel = '.' + name;
            var inverse = inv;
            var func = function(a, b) {
                var a_val = $(sel, a).text().toLowerCase().replace(/ö/g, 'ozzz').replace(/ü/g, 'uzzz').replace(/ä/g, 'azzz').replace(/ß/g, 'szzz');
                var b_val = $(sel, b).text().toLowerCase().replace(/ö/g, 'ozzz').replace(/ü/g, 'uzzz').replace(/ä/g, 'azzz').replace(/ß/g, 'szzz');
                if (inverse) {
                    return a_val < b_val ? 1 : -1;
                } else {
                    return b_val < a_val ? 1 : -1;
                }
            }
            return func;
        },
        
        // sort listings binder
        listing_sort_binder: function(context) {
            var sort_links = $('.columnsorting a', context);
            sort_links.unbind().bind('click', function(event) {
                bdajax.spinner.show();
                event.preventDefault();
                var elem = $(this);
                var inv = elem.hasClass('inv');
                sort_links.removeClass('default')
                          .removeClass('inv')
                          .removeClass('asc')
                          .removeClass('desc');
                var cont = $('.columnitems', elem.parent().parent().parent());
                if (inv) {
                    elem.addClass('asc');
                } else {
                    elem.addClass('inv').addClass('desc');
                }
                var sortname = elem.attr('href');
                var sortfunc = ugm.listing_sort_func(sortname, inv);
                var sorted = $('ul li', cont).sort(sortfunc);
                $('ul', cont).empty().append(sorted);
                ugm.left_listing_nav_binder(cont);
                //ugm.right_listing_nav_binder(cont);
                ugm.listing_actions_binder(cont);
                ugm.scroll_listings_to_selected();
                bdajax.spinner.hide();
            });
            $('.columnsorting a.default', context).trigger('click');
        }
    };
    
})(jQuery);
