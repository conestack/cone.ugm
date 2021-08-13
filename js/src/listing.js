import $ from 'jquery';
import ts from 'treibstoff';
import cone from 'cone';

class PrincipalAdding {

    static initialize(context) {
        $('div.add_button button', context).on('click', function() {
            $('.left_column ul.leftlisting li').removeClass('selected');
        });
    }
}

class PrincipalListing {

    static initialize(context) {
    }

    // bind listing item actions
    listing_actions_binder(context) {
        // bind delete actions
        $('div.columnitems div.actions a.delete_item', context)
            .off()
            .on('click', ugm.actions.delete_item);

        // bind disabled delete actions
        $('div.columnitems div.actions a.delete_item_disabled', context)
            .off()
            .on('click', function(evt) {
                evt.preventDefault();
            });
        // bind add actions
        $('div.columnitems div.actions a.add_item', context)
            .off()
            .on('click', ugm.actions.listing_add_item);

        // bind disabled add actions
        $('div.columnitems div.actions a.add_item_disabled', context)
            .off()
            .on('click', function(evt) {
                evt.preventDefault();
            });
        // bind remove actions
        $('div.columnitems div.actions a.remove_item', context)
            .off()
            .on('click', ugm.actions.listing_remove_item);
        // bind disabled remove actions
        $('div.columnitems div.actions a.remove_item_disabled', context)
            .off()
            .on('click', function(evt) {
                evt.preventDefault();
            });
    }

    // bind listing filter
    listing_filter_binder(context) {
        var filter_selector = 'div.column_filter input';
        var filter_name = 'filter';
        cone.BatchedItems.bind_search(
            context,
            filter_selector,
            filter_name
        );
    }

    // bind related items filter
    // XXX: changed to list_all, wait for group in group to fix naming
    listing_related_binder(context) {
        $('div.column_limit input.list_all', context)
            .off()
            .on('click', ugm.listing_related_cb);
    }

    // callback when related filter gets toggled
    listing_related_cb(evt) {
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

    // reset selcted item in listing
    reset_listing_selected(li) {
        $('li', li.parent()).removeClass('selected');
        li.addClass('selected');
    }
}

class LeftPrincipalListing extends PrincipalListing {

    // bind left listing trigger
    left_listing_nav_binder(context) {
        $('ul.leftlisting li', context)
            .off()
            .on('click', this.left_listing_nav_cb.bind(this));
    }

    // left listing trigger callback
    left_listing_nav_cb(evt) {
        var li = $(evt.currentTarget);
        this.reset_listing_selected(li);

        // perform action manually
        var target = ts.parse_target(li.attr('ajax:target'));
        bts.ajax.action({
            name: 'rightcolumn',
            selector: '.right_column',
            mode: 'replace',
            url: target.url,
            params: target.params
        });
        return false;
    }
}

class LeftPrincipalListing extends PrincipalListing {

    // bind right listing trigger
    right_listing_nav_binder(context) {
        $('ul.rightlisting li', context)
            .off()
            .on('click', this.right_listing_nav_cb.bind(this));
    }

    // right listing trigger callback
    right_listing_nav_cb(evt) {
        var li = $(evt.currentTarget);
        this.reset_listing_selected(li);

        // reload context sensitiv tiles and context with new target
        var target = li.attr('ajax:target');
        ts.ajax.trigger('contextchanged', '.contextsensitiv', target);
        ts.ajax.trigger('contextchanged', '#content', target);
        return false;
    }
}
