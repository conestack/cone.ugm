import logging
from pyramid.security import has_permission
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.ugm.model.users import Users
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing


logger = logging.getLogger('cone.ugm')


@tile('leftcolumn', 'templates/left_column.pt',
      interface=Users, permission='view')
class UsersLeftColumn(Tile):

    add_label = u"Add User"

    @property
    def add_target(self):
        return make_url(self.request,
                        node=self.model.root['users'],
                        query=make_query(factory=u'user'))
    
    @property
    def can_add(self):
        return has_permission('add', self.model, self.request)


@tile('rightcolumn', interface=Users, permission='view')
class UsersRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=Users, permission='view')
class UsersColumnListing(ColumnListing):

    slot = 'leftlisting'
    list_columns = ColumnListing.user_list_columns
    css = 'users'
    batchname = 'leftbatch'

    @property
    def current_id(self):
        return getattr(self.request, '_curr_listing_id', None)

    @property
    def query_items(self):
        can_delete = has_permission('delete', self.model, self.request)
        try:
            col_1_attr, col_2_attr, col_3_attr, sort_attr = self.user_attrs
            ret = list()
            attrlist = [col_1_attr, col_2_attr, col_3_attr]
            users = self.model.backend
            result = users.search(criteria=None, attrlist=attrlist)
            for key, attrs in result:
                target = make_url(self.request,
                                  node=self.model,
                                  resource=key)
                
                actions = list()
                if can_delete:
                    action_id = 'delete_item'
                    action_title = 'Delete User'
                    delete_action = self.create_action(
                        action_id, True, action_title, target)
                    actions = [delete_action]
                
                val_1 = self.extract_raw(attrs, col_1_attr)
                val_2 = self.extract_raw(attrs, col_2_attr)
                val_3 = self.extract_raw(attrs, col_3_attr)
                sort = self.extract_raw(attrs, sort_attr)
                content = self.item_content(val_1, val_2, val_3)
                current = self.current_id == key
                item = self.create_item(
                    sort, target, content, current, actions)
                ret.append(item)
            return ret
        except Exception, e:
            logger.error(str(e))
        return list()