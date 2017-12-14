from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.tile import Tile
from cone.tile import tile
from cone.ugm.browser.columns import Column
from cone.ugm.browser.listing import PrincipalsListing
from cone.ugm.model.users import Users
from pyramid.i18n import TranslationStringFactory
from pyramid.security import has_permission
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@tile('leftcolumn', 'templates/principals_left_column.pt',
      interface=Users, permission='view')
class UsersLeftColumn(Tile):
    add_label = _('add_user', default='Add User')

    @property
    def add_target(self):
        return make_url(
            self.request,
            node=self.model.root['users'],
            query=make_query(factory=u'user')
        )

    @property
    def can_add(self):
        return has_permission('add_user', self.model, self.request)


@tile('rightcolumn', 'templates/principals_right_column.pt',
      interface=Users, permission='view')
class UsersRightColumn(Column):

    @property
    def principal_id(self):
        return self.request.params.get('pid')

    @property
    def principal_form(self):
        return self._render(self.model[self.principal_id], 'editform')

    @property
    def principal_target(self):
        return make_url(self.request, node=self.model[self.principal_id])


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
    delete_label = _('delete_user', default='Delete User')
    delete_permission = 'delete_user'

    @property
    def current_id(self):
        return self.request.params.get('pid')
