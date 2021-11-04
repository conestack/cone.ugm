from cone.app import compat
from cone.app.browser.batch import Batch
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.app.browser.utils import nodepath
from cone.app.browser.utils import request_property
from cone.tile import Tile
from cone.ugm.utils import general_settings
from node.utils import safe_decode
from pyramid.i18n import TranslationStringFactory
from yafowil.utils import Tag
import logging
import natsort


tag = Tag(lambda x: x)


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


class ColumnListingBatch(Batch):
    """Column listing batch.
    """

    def __init__(self, listing):
        self.listing = listing
        self.name = listing.batchname
        self.items = listing.listing_items
        self.slicesize = listing.slicesize

    @property
    def display(self):
        return len(self.vocab) > 1

    @property
    def vocab(self):
        ret = list()
        path = nodepath(self.model)
        count = len(self.items)
        pages = count // self.slicesize
        if count % self.slicesize != 0:
            pages += 1
        current = self.listing.current_page
        for i in range(pages):
            ret.append({
                'page': '%i' % (i + 1),
                'current': current == i,
                'visible': True,
                'target': self.listing.batch_target(path, i)
            })
        return ret


class ColumnListing(Tile):
    """Abstract column listing.
    """
    current_id = None
    slot = None
    list_columns = []
    css = ''
    slicesize = 15
    batchname = ''
    default_order = 'asc'
    display_filter = True
    display_limit = False
    display_limit_checked = False

    @property
    def ajax_action(self):
        return 'columnlisting'

    @property
    def ajax_event(self):
        return '{}:{}'.format(
            self.batch.trigger_event,
            self.batch.trigger_selector
        )

    @property
    def sortheader(self):
        ret = list()
        for cid, name in self.list_columns.items():
            cur_sort = self.sort_column
            cur_order = self.sort_order
            selected = cur_sort == cid
            alter = selected and cur_order == 'asc'
            order = alter and 'desc' or 'asc'
            ret.append({
                'title': name,
                'order': order if selected else '',
                'target': self.sort_target(cid, order)
            })
        return ret

    def unquoted_param_value(self, name):
        value = self.request.params.get(name)
        if value:
            value = value.encode('utf-8') if compat.IS_PY2 else value
            value = compat.unquote(value)
            value = value.decode('utf-8') if compat.IS_PY2 else value
        return value

    def filter_value_or_default(self, name):
        value = self.unquoted_param_value(name)
        return value if value else _('filter_listing', default='filter listing')

    @property
    def filter_target(self):
        query = make_query(dict(sort=self.sort_column, order=self.sort_order))
        return safe_decode(make_url(self.request, node=self.model, query=query))

    @property
    def filter_term(self):
        return self.unquoted_param_value('filter')

    @property
    def filter_value(self):
        return self.filter_value_or_default('filter')

    @property
    def default_sort(self):
        return self.list_columns.keys()[0]

    @property
    def sort_column(self):
        return self.request.params.get('sort', self.default_sort)

    @property
    def sort_order(self):
        return self.request.params.get('order', self.default_order)

    def sort_target(self, sort, order):
        query = make_query(
            filter=self.filter_term,
            b_page=self.current_page,
            sort=sort,
            order=order)
        return safe_decode(make_url(self.request, node=self.model, query=query))

    @property
    def current_page(self):
        return int(self.request.params.get('b_page', '0'))

    @request_property
    def batch(self):
        return ColumnListingBatch(self)

    @property
    def rendered_batch(self):
        return self.batch(self.model, self.request)

    def batch_target(self, path, b_page):
        query = make_query(
            b_page=str(b_page),
            filter=self.filter_term,
            sort=self.sort_column,
            order=self.sort_order)
        return safe_decode(make_url(self.request, path=path, query=query))

    @property
    def slice(self):
        start = self.current_page * self.slicesize
        end = start + self.slicesize
        return start, end

    @property
    def items(self):
        start, end = self.slice
        items = self.listing_items
        inv = self.sort_order == 'desc'
        items = natsort.natsorted(
            items,
            key=lambda x: x['sort_by'],
            reverse=inv,
            alg=natsort.ns.IC
        )
        return items[start:end]

    @property
    def listing_items(self):
        """Return list of dicts like:

        {
            'target': u'http://example.com/foo',
            'content': u'Head Column content',
            'sort_by: u'Sort value',
            'current': False,
            'actions': [
                {
                    'id': 'action_id',
                    'enabled': True,
                    'title': 'Action Title',
                    'target': u'http://example.com/foo',
                }
            ],
        }
        """
        raise NotImplementedError(
            'Abstract ``ColumnListing`` does not implement ``listing_items``')

    def item_content(self, *args):
        ret = u''
        pt = 0
        for arg in args:
            pt += 1
            ret += tag('div', '%s&nbsp;' % arg, class_='sort_col_%i' % pt)
        return ret

    def create_item(self, sort, target, content, current, actions):
        return {
            'sort_by': sort,
            'target': target,
            'content': content,
            'current': current,
            'actions': actions,
        }

    def create_action(self, aid, enabled, title, target):
        return {
            'id': aid,
            'enabled': enabled,
            'title': title,
            'target': target,
        }

    def extract_raw(self, attrs, name):
        raw = attrs.get(name)
        if type(raw) in compat.ITER_TYPES:
            return raw[0]
        return raw and raw or ''

    ############################################################
    # XXX: users and groups related info to dedicated subclasses

    # USERS RELATED

    @property
    def user_list_columns(self):
        settings = general_settings(self.model)
        return settings.attrs.users_listing_columns

    @property
    def user_attrs(self):
        settings = general_settings(self.model)
        return settings.attrs.users_listing_columns.keys()

    @property
    def user_localmanager_ids(self):
        if not self.model.local_manager_consider_for_user:
            return None
        return self.model.local_manager_target_uids

    @property
    def user_default_sort_column(self):
        settings = general_settings(self.model)
        attrs = self.user_attrs
        sort = settings.attrs.users_listing_default_column
        if sort not in attrs:
            return attrs[0]
        return sort

    # GROUPS RELATED

    @property
    def group_list_columns(self):
        settings = general_settings(self.model)
        return settings.attrs.groups_listing_columns

    @property
    def group_attrs(self):
        settings = general_settings(self.model)
        return settings.attrs.groups_listing_columns.keys()

    @property
    def group_localmanager_ids(self):
        if not self.model.local_manager_consider_for_user:
            return None
        return self.model.local_manager_target_gids

    @property
    def group_default_sort_column(self):
        settings = general_settings(self.model)
        attrs = self.group_attrs
        sort = settings.attrs.groups_listing_default_column
        if sort not in attrs:
            return attrs[0]
        return sort

    # XXX: end move
    ############################################################


class PrincipalsListing(ColumnListing):
    """Column listing for principals.
    """
    delete_label = _('delete_principal', default='Delete Principal')
    delete_permission = 'delete_principal'  # inexistent permission
    listing_attrs = []
    localmanager_ids = None
    sort_attr = None

    @request_property
    def listing_items(self):
        can_delete = self.request.has_permission(
            self.delete_permission,
            self.model
        )
        try:
            ret = list()
            localmanager_ids = self.localmanager_ids
            # if localmanager ids not none but empty, no access to any
            # principals
            if localmanager_ids is not None and not localmanager_ids:
                return ret
            attrlist = self.listing_attrs
            sort_attr = self.sort_attr
            # build criteria from filter term
            criteria = None
            filter_term = self.filter_term
            if filter_term:
                criteria = dict()
                for attr in attrlist:
                    criteria[attr] = filter_term
            principals = self.model.backend
            result = principals.search(
                criteria=criteria,
                attrlist=attrlist,
                or_search=True
            )
            for key, attrs in result:
                # reduce result by localmanager ids if not None
                if localmanager_ids is not None and key not in localmanager_ids:
                    continue
                actions = list()
                if can_delete:
                    action_id = 'delete_item'
                    action_title = self.delete_label
                    action_target = make_url(
                        self.request,
                        node=self.model,
                        resource=key
                    )
                    delete_action = self.create_action(
                        action_id,
                        True,
                        action_title,
                        action_target
                    )
                    actions = [delete_action]
                vals = [self.extract_raw(attrs, attr) for attr in attrlist]
                sort = self.extract_raw(attrs, sort_attr)
                query = make_query(
                    pid=key,
                    came_from=make_url(self.request, node=self.model)
                )
                target = make_url(self.request, node=self.model, query=query)
                content = self.item_content(*vals)
                current = self.current_id == key
                ret.append(self.create_item(
                    sort,
                    target,
                    content,
                    current,
                    actions
                ))
            return ret
        except Exception:
            logger.exception('Failed to query listing items')
        return list()
