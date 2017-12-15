from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.app.browser.utils import request_property
from cone.app.browser.utils import safe_decode
from cone.tile import Tile
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.model.utils import ugm_groups
from cone.ugm.model.utils import ugm_users
from pyramid.i18n import TranslationStringFactory
from pyramid.security import has_permission
from yafowil.utils import Tag
import logging
import types
import urllib2
import uuid


tag = Tag(lambda x: x)

logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


class ColumnListing(Tile):
    """Abstract column listing.
    """
    current_id = None
    slot = None
    list_columns = []
    css = ''
    slicesize = 5
    batchname = ''
    default_sort = None
    default_order = None
    display_filter = True
    display_limit = False

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
        for cid, name in self.list_columns:
            ret.append({
                'id': 'sort_%s' % cid,
                'default': False,
                'name': name,
            })
        ret[0]['default'] = True
        return ret

    @property
    def filter_target(self):
        query = make_query(dict(sort=self.sort_column, order=self.sort_order))
        return safe_decode(make_url(self.request, node=self.model, query=query))

    @property
    def filter_term(self):
        term = self.request.params.get('column_filter')
        return urllib2.unquote(
            term.encode('utf-8')).decode('utf-8') if term else term

    @property
    def filter_value(self):
        term = self.filter_term
        if not term:
            return _('filter_listing', default='filter listing')
        return term

    @property
    def sort_column(self):
        return self.request.params.get('sort', self.default_sort)

    @property
    def sort_order(self):
        return self.request.params.get('order', self.default_order)

    @property
    def current_page(self):
        return int(self.request.params.get('b_page', '0'))

    @request_property
    def batch(self):
        return ColumnBatch(self.batchname, self.query_items, self.slicesize)

    @property
    def rendered_batch(self):
        return self.batch(self.model, self.request)

    @property
    def slice(self):
        start = self.current_page * self.slicesize
        end = start + self.slicesize
        return start, end

    @property
    def items(self):
        start, end = self.slice
        items = self.query_items
        items = sorted(items, key=lambda x: x['sort_by'].lower())
        return items[start:end]

    @property
    def query_items(self):
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
            'Abstract ``ColumnListing`` does not implement ``items``')

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
        if type(raw) in [types.ListType, types.TupleType]:
            return raw[0]
        return raw and raw or ''

    def calc_list_columns(self, defs):
        ret = list()
        i = 1
        for val in defs.values():
            ret.append(('col_%i' % i, val))
            i += 1
        return ret

    ############################################################
    # XXX: users and groups related info to dedicated subclasses

    @property
    def user_attrs(self):
        settings = ugm_users(self.model)
        return settings.attrs.users_listing_columns.keys()

    @property
    def group_attrs(self):
        settings = ugm_groups(self.model)
        return settings.attrs.groups_listing_columns.keys()

    @property
    def user_listing_criteria(self):
        term = self.filter_term
        if term:
            pass
        if not self.model.local_manager_consider_for_user:
            return None
        ids = self.model.local_manager_target_uids
        if not ids:
            ids = [str(uuid.uuid4())]  # ensure criteria forces empty result
        return dict(id=ids)

    @property
    def group_listing_criteria(self):
        term = self.filter_term
        if term:
            pass
        if not self.model.local_manager_consider_for_user:
            return None
        ids = self.model.local_manager_target_gids
        if not ids:
            ids = [str(uuid.uuid4())]  # ensure criteria forces empty result
        return dict(id=ids)

    @property
    def user_list_columns(self):
        settings = ugm_users(self.model)
        defs = settings.attrs.users_listing_columns
        return self.calc_list_columns(defs)

    @property
    def group_list_columns(self):
        settings = ugm_groups(self.model)
        defs = settings.attrs.groups_listing_columns
        return self.calc_list_columns(defs)

    @property
    def user_default_sort_column(self):
        settings = ugm_users(self.model)
        attrs = self.user_attrs
        sort = settings.attrs.users_listing_default_column
        if not sort in attrs:
            return attrs[0]
        return sort

    @property
    def group_default_sort_column(self):
        settings = ugm_groups(self.model)
        attrs = self.group_attrs
        sort = settings.attrs.groups_listing_default_column
        if not sort in attrs:
            return attrs[0]
        return sort

    # XXX: end move
    ###########################################################################


class PrincipalsListing(ColumnListing):
    """Column listing for principals.
    """
    delete_label = _('delete_principal', default='Delete Principal')
    delete_permission = 'delete_principal'  # inexistent permission
    listing_attrs = []
    listing_criteria = None
    sort_attr = None

    @request_property
    def query_items(self):
        can_delete = has_permission(
            self.delete_permission,
            self.model,
            self.request)
        try:
            attrlist = self.listing_attrs
            criteria = self.listing_criteria
            sort_attr = self.sort_attr

            print attrlist
            print criteria
            print sort_attr

            ret = list()
            principals = self.model.backend
            result = principals.search(
                criteria=criteria,
                attrlist=attrlist,
                or_search=True)
            for key, attrs in result:
                query = make_query(
                    pid=key,
                    came_from=make_url(self.request, node=self.model))
                target = make_url(self.request, node=self.model, query=query)
                actions = list()
                if can_delete:
                    action_id = 'delete_item'
                    action_title = self.delete_label
                    delete_action = self.create_action(
                        action_id, True, action_title, target)
                    actions = [delete_action]
                vals = [self.extract_raw(attrs, attr) for attr in attrlist]
                sort = self.extract_raw(attrs, sort_attr)
                content = self.item_content(*vals)
                current = self.current_id == key
                ret.append(self.create_item(
                    sort, target, content, current, actions))
            return ret
        except Exception as e:
            logger.error(str(e))
        return list()
