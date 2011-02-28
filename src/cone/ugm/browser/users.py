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


@tile('columnbatch', interface=IUsers, permission='view')
class UsersColumnBatch(ColumnBatch):
    pass


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IUsers, permission='view')
class UsersColumnListing(ColumnListing):
    
    slot = 'leftlisting'
    
    @property
    def current_id(self):
        return self.request.get('_curr_listing_id')
    
    @property
    def items(self):
        ret = list()
        result = self.model.ldap_users.search(criteria=None,
                                              attrlist=['cn', 'sn' , 'mail'])
        for entry in result:
            target = make_url(self.request,
                              node=self.model,
                              resource=entry[0])
            attrs = entry[1]
            
            # XXX: from config
            head = '<span class="sort_name">%s&nbsp;</span>' + \
                   '<span class="sort_surname">%s&nbsp;</span>' + \
                   '<span class="sort_email">&lt;%s&gt;</span>'
            cn = attrs.get('cn')
            cn = cn and cn[0] or ''
            sn = attrs.get('sn')
            sn = sn and sn[0] or ''
            mail = attrs.get('mail')
            mail = mail and mail[0] or ''
            head = head % (cn, sn, mail)
            ret.append({
                'target': target,
                'head': head,
                'current': self.current_id == entry[0] and True or False,
                'actions': [
                    {
                        'id': 'delete_item',
                        'enabled': True,
                        'title': 'Delete User',
                        'target': target
                    }
                ]
            })
        return ret