from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.ugm.model.interfaces import IGroups
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing


@tile('leftcolumn', 'templates/left_column.pt',
      interface=IGroups, permission='view')
class GroupsLeftColumn(Tile):

    add_label = u"Add Group"

    @property
    def add_target(self):
        return make_url(self.request,
                        node=self.model.root['groups'],
                        query=make_query(factory=u'group'))


@tile('rightcolumn', interface=IGroups, permission='view')
class GroupsRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IGroups, permission='view')
class GroupsColumnListing(ColumnListing):

    slot = 'leftlisting'
    list_columns = ['name']
    css = 'groups'
    batchname = 'leftbatch'

    @property
    def current_id(self):
        return self.request.get('_curr_listing_id')

    @property
    def query_items(self):
        name_attr = self.group_attrs
        ret = list()
        result = self.model.ldap_groups.search(criteria=None,
                                               attrlist=[name_attr])
        for key, attrs in result:
            target = make_url(self.request,
                              node=self.model,
                              resource=key)
            name = self.extract_raw(attrs, name_attr)
            ret.append({
                'sort_by': name,
                'target': target,
                'head': self.itemhead(name),
                'current': self.current_id == key and True or False,
                'actions': [
                    {
                        'id': 'delete_item',
                        'enabled': True,
                        'title': 'Delete Group',
                        'target': target
                    }
                ]
            })
        return ret
