from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.ugm.model.interfaces import IUsers
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing


@tile('leftcolumn', 'templates/left_column.pt',
      interface=IUsers, permission='view')
class UsersLeftColumn(Tile):

    add_label = u"Add User"

    @property
    def add_target(self):
        return make_url(self.request,
                        node=self.model.root['users'],
                        query=make_query(factory=u'user'))


@tile('rightcolumn', interface=IUsers, permission='view')
class UsersRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IUsers, permission='view')
class UsersColumnListing(ColumnListing):

    slot = 'leftlisting'
    list_columns = ColumnListing.user_list_columns
    css = 'users'
    batchname = 'leftbatch'

    @property
    def current_id(self):
        return self.request.get('_curr_listing_id')

    @property
    def query_items(self):
        col_1_attr, col_2_attr, col_3_attr, sort_attr = self.user_attrs
        ret = list()
        try:
            attrlist = [col_1_attr, col_2_attr, col_3_attr]
            users = self.model.ldap_users
            result = users.search(criteria=None, attrlist=attrlist)
        except Exception, e:
            print 'Query Failed: ' + str(e)
            return []
        for key, attrs in result:
            target = make_url(self.request,
                              node=self.model,
                              resource=key)
            
            action_id = 'delete_item'
            action_title = 'Delete User'
            delete_action = self.create_action(
                action_id, True, action_title, target)
            
            val_1 = self.extract_raw(attrs, col_1_attr)
            val_2 = self.extract_raw(attrs, col_2_attr)
            val_3 = self.extract_raw(attrs, col_3_attr)
            sort = self.extract_raw(attrs, sort_attr)
            content = self.item_content(val_1, val_2, val_3)
            current = self.current_id == key
            item = self.create_item(
                sort, target, content, current, [delete_action])
            ret.append(item)
        return ret
