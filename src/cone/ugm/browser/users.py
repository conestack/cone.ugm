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
    list_columns = ['name', 'surname', 'email']
    css = 'users'

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
            cn = attrs.get('cn') and attrs.get('cn')[0] or ''
            sn = attrs.get('sn') and attrs.get('sn')[0] or ''
            mail = attrs.get('mail') and attrs.get('mail')[0] or ''
            ret.append({
                'target': target,
                'head': self._itemhead(cn, sn, mail),
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
