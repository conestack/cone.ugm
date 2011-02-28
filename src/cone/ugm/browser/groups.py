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


@tile('columnbatch', interface=IGroups, permission='view')
class GroupsColumnBatch(ColumnBatch):
    pass


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IGroups, permission='view')
class GroupsColumnListing(ColumnListing):
    
    slot = 'leftlisting'
    
    @property
    def current_id(self):
        return self.request.get('_curr_listing_id')
    
    @property
    def sortheader(self):
        ret = list()
        for id in ['name']:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': id,
            })
        ret[0]['default'] = True
        return ret
    
    @property
    def items(self):
        ret = list()
        result = self.model.ldap_groups.search(criteria=None,
                                               attrlist=['cn'])
        for entry in result:
            target = make_url(self.request,
                              node=self.model,
                              resource=entry[0])
            attrs = entry[1]
            
            # XXX: from config
            head = '<span class="sort_name">%s&nbsp;</span>'
            cn = attrs.get('cn')
            cn = cn and cn[0] or ''
            head = head % cn
            ret.append({
                'target': target,
                'head': head,
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
        return ret