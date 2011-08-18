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
from cone.ugm.model.groups import Groups
from cone.ugm.browser.listing import PrincipalsListing


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
    
    @property
    def can_add(self):
        return has_permission('add', self.model, self.request)


@tile('rightcolumn', interface=Groups, permission='view')
class GroupsRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=Groups, permission='view')
class GroupsColumnListing(PrincipalsListing):

    slot = 'leftlisting'
    list_columns = PrincipalsListing.group_list_columns
    listing_attrs = PrincipalsListing.group_attrs
    sort_attr = PrincipalsListing.group_default_sort_column
    css = 'groups'
    batchname = 'leftbatch'
    delete_label = 'Delete Group'

    @property
    def current_id(self):
        return getattr(self.request, '_curr_listing_id', None)