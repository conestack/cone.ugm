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
        ret = list()
        result = self.model.ldap_groups.search(criteria=None,
                                               attrlist=['cn'])
        for entry in result:
            target = make_url(self.request,
                              node=self.model,
                              resource=entry[0])
            attrs = entry[1]
            cn = attrs.get('cn') and attrs.get('cn')[0] or ''
            ret.append({
                'cn': cn, # XXX: hack
                'target': target,
                'head': self._itemhead(cn),
                'current': self.current_id == entry[0] and True or False,
                'actions': [
                    {
                        'id': 'delete_item',
                        'enabled': True,
                        'title': 'Delete Group',
                        'target': target
                    }
                ]
            })
        ret = sorted(ret, key=lambda x: x['cn'].lower())
        return ret
