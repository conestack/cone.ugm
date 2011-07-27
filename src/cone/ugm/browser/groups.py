import logging
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.ugm.model.groups import Groups
from cone.ugm.browser.listing import ColumnListing


logger = logging.getLogger('cone.ugm')


@tile('leftcolumn', 'templates/left_column.pt',
      interface=Groups, permission='view')
class GroupsLeftColumn(Tile):

    add_label = u"Add Group"

    @property
    def add_target(self):
        return make_url(self.request,
                        node=self.model.root['groups'],
                        query=make_query(factory=u'group'))


@tile('rightcolumn', interface=Groups, permission='view')
class GroupsRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=Groups, permission='view')
class GroupsColumnListing(ColumnListing):

    slot = 'leftlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    batchname = 'leftbatch'

    @property
    def current_id(self):
        return getattr(self.request, '_curr_listing_id', None)

    @property
    def query_items(self):
        try:
            col_1_attr = self.group_attrs
            ret = list()
            result = self.model.backend.search(
                criteria=None,
                attrlist=[col_1_attr],
                )
            for key, attrs in result:
                target = make_url(self.request,
                                  node=self.model,
                                  resource=key)
                action_id = 'delete_item'
                action_title = 'Delete Group'
                delete_action = self.create_action(
                    action_id, True, action_title, target)
                
                val_1 = self.extract_raw(attrs, col_1_attr)
                content = self.item_content(val_1)
                current = self.current_id == key
                item = self.create_item(
                    val_1, target, content, current, [delete_action])
                ret.append(item)
            return ret
        except Exception, e:
            logger.error(str(e))
        return list()