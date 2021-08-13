import $ from 'jquery';
import ts from 'treibstoff';
import cone from 'cone';
import {PrincipalActions} from './actions.js';

export class PrincipalListing {

    static initialize(context) {
        // bind listing filter
        cone.BatchedItems.bind_search(
            context,
            'div.column_filter input',
            'filter'
        );

        // bind principal listings
        new LeftPrincipalListing(context);
        new RightPrincipalListing(context);
    }

    constructor() {
        this.actions = new PrincipalActions;
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

export class LeftPrincipalListing extends PrincipalListing {

    constructor(context) {
        super();

        // bind add principal button
        let add_btn = $('div.add_button button', context);
        add_btn.off('click').on('click', this.add_principal.bind(this));

        // bind listing item actions
        let actions = $('div.columnitems div.actions', context);

        let delete_actions = $('a.delete_item', actions);
        delete_actions.off().on('click', this.actions.delete_item);

        let delete_actions_disabled = $('a.delete_item_disabled', actions);
        delete_actions_disabled.off().on('click', this.noop);

        // bind item navigation
        let listing_items = $('ul.leftlisting li', context);
        listing_items.off().on('click', this.show_item.bind(this));
    }

    add_principal(evt) {
        evt.preventDefault();
        evt.stopPropagation();

        let listing = $('.left_column ul.leftlisting');
        this.reset_selected(listing);

        let elem = $(evt.currentTarget),
            target = ts.ajax.parse_target(elem.attr('ajax:target'));
        ts.ajax.action({
            name: 'add',
            selector: '.right_column',
            mode: 'inner',
            url: target.url,
            params: target.params
        })
    }

    show_item(evt) {
        let li = $(evt.currentTarget);
        this.set_selected(li);

        let target = ts.ajax.parse_target(li.attr('ajax:target'));
        ts.ajax.action({
            name: 'rightcolumn',
            selector: '.right_column',
            mode: 'replace',
            url: target.url,
            params: target.params
        });
        return false;
    }
}

export class RightPrincipalListing extends PrincipalListing {

    constructor(context) {
        super();

        // bind listing item actions
        let actions = $('div.columnitems div.actions', context);

        let add_actions = $('a.add_item', actions);
        add_actions.off().on('click', this.actions.add_item);

        let add_actions_disabled = $('a.add_item_disabled', actions);
        add_actions_disabled.off().on('click', this.noop);

        let remove_actions = $('a.remove_item', actions);
        remove_actions.off().on('click', this.actions.remove_item);

        let remove_actions_disabled = $('a.remove_item_disabled', actions);
        remove_actions_disabled.off().on('click', this.noop);

        // bind item navigation
        let listing_items = $('ul.rightlisting li', context);
        listing_items.off().on('click', this.show_item.bind(this));

        // bind list all action
        // XXX: changed to list_all, wait for group in group to fix naming
        let list_all_action = $('div.column_limit input.list_all', context);
        list_all_action.off().on('click', this.list_related.bind(this));
    }

    show_item(evt) {
        let li = $(evt.currentTarget);
        this.set_selected(li);

        // reload context sensitiv tiles and context with new target
        let target = li.attr('ajax:target');
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
        let target = ts.ajax.parse_target(elem.attr('ajax:target'));
        ts.ajax.action({
            name: action,
            selector: 'div.right_column .columnlisting',
            mode: 'replace',
            url: target.url,
            params: target.params
        });
    }
}
