import logging
from pyramid.security import has_permission
from pyramid.i18n import TranslationStringFactory
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.ugm.model.users import Users
from cone.ugm.browser.listing import PrincipalsListing

logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@tile('leftcolumn', 'templates/left_column.pt',
      interface=Users, permission='view')
class UsersLeftColumn(Tile):

    add_label = _('add_user', 'Add User')

    @property
    def add_target(self):
        return make_url(self.request,
                        node=self.model.root['users'],
                        query=make_query(factory=u'user'))
    
    @property
    def can_add(self):
        return has_permission('add_user', self.model, self.request)


@tile('rightcolumn', interface=Users, permission='view')
class UsersRightColumn(Tile):

    def render(self):
        return u'<div class="column right_column">&nbsp;</div>'


@tile('columnlisting', 'templates/column_listing.pt',
      interface=Users, permission='view')
class UsersColumnListing(PrincipalsListing):

    slot = 'leftlisting'
    list_columns = PrincipalsListing.user_list_columns
    listing_attrs = PrincipalsListing.user_attrs
    listing_criteria = PrincipalsListing.user_listing_criteria
    sort_attr = PrincipalsListing.user_default_sort_column
    css = 'users'
    batchname = 'leftbatch'
    delete_label = _('delete_user', 'Delete User')
    delete_permission = 'delete_user'

    @property
    def current_id(self):
        return getattr(self.request, '_curr_listing_id', None)