import types
import logging
from pyramid.security import has_permission
from yafowil.utils import Tag
from cone.tile import Tile
from cone.app.browser.utils import make_url
from cone.ugm.model.utils import (
    ugm_users,
    ugm_groups,
)
from cone.ugm.browser.batch import ColumnBatch

tag = Tag(lambda x: x)

logger = logging.getLogger('cone.ugm')


class ColumnListing(Tile):
    """Abstract column listing.
    """

    current_id = None
    slot = None
    list_columns = []
    css = ''
    # XXX: Batch is effectively disabled, if enabled, the sorting
    # needs to be fixed before slicing
    slicesize = 100000
    batchname = ''

    @property
    def ajax_action(self):
        return 'columnlisting'

    @property
    def sortheader(self):
        ret = list()
        for id, name in self.list_columns:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': name,
            })
        ret[0]['default'] = True
        return ret

    @property
    def batch(self):
        return ColumnBatch(self.batchname,
                           self.query_items,
                           self.slicesize)(self.model, self.request)

    @property
    def slice(self):
        current = int(self.request.params.get('b_page', '0'))
        start = current * self.slicesize
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
        raise NotImplementedError(                          #pragma NO COVERAGE
            u"Abstract ``ColumnListing`` does not "         #pragma NO COVERAGE
            u"implement ``items`` property")                #pragma NO COVERAGE

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

    def create_action(self, id, enabled, title, target):
        return {
            'id': id,
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
    
    @property
    def user_attrs(self):
        """XXX: not generic, move
        """
        settings = ugm_users(self.model)
        return settings.attrs.users_listing_columns.keys()

    @property
    def group_attrs(self):
        """XXX: not generic, move
        """
        settings = ugm_groups(self.model)
        return settings.attrs.groups_listing_columns.keys()

    @property
    def user_list_columns(self):
        """XXX: not generic, move
        """
        settings = ugm_users(self.model)
        defs = settings.attrs.users_listing_columns
        return self.calc_list_columns(defs)

    @property
    def group_list_columns(self):
        """XXX: not generic, move
        """
        settings = ugm_groups(self.model)
        defs = settings.attrs.groups_listing_columns
        return self.calc_list_columns(defs)
    
    @property
    def user_default_sort_column(self):
        """XXX: not generic, move
        """
        settings = ugm_users(self.model)
        attrs = self.user_attrs
        sort = settings.attrs.users_listing_default_column
        if not sort in attrs:
            return attrs[0]
        return sort
    
    @property
    def group_default_sort_column(self):
        """XXX: not generic, move
        """
        settings = ugm_groups(self.model)
        attrs = self.group_attrs
        sort = settings.attrs.groups_listing_default_column
        if not sort in attrs:
            return attrs[0]
        return sort


class PrincipalsListing(ColumnListing):
    """Column listing for principals.
    """
    delete_label = 'Delete Principal'
    listing_attrs = []
    sort_attr = None
    
    @property
    def query_items(self):
        can_delete = has_permission('delete', self.model, self.request)
        try:
            attrlist = self.listing_attrs
            sort_attr = self.sort_attr
            ret = list()
            users = self.model.backend
            result = users.search(criteria=None, attrlist=attrlist)
            for key, attrs in result:
                target = make_url(self.request,
                                  node=self.model,
                                  resource=key)
                
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
                item = self.create_item(
                    sort, target, content, current, actions)
                ret.append(item)
            return ret
        except Exception, e:
            logger.error(str(e))
        return list()