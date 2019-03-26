from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.tile import Tile
from cone.tile import tile
from cone.ugm.browser.columns import Column
from cone.ugm.browser.listing import PrincipalsListing
from cone.ugm.model.users import Users
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@tile(
    name='leftcolumn',
    path='templates/principals_left_column.pt',
    interface=Users,
    permission='view')
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
        return self.request.has_permission('add_user', self.model)


@tile(
    name='rightcolumn',
    path='templates/principals_right_column.pt',
    interface=Users,
    permission='view')
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


@tile(
    name='columnlisting',
    path='templates/column_listing.pt',
    interface=Users,
    permission='view')
class UsersColumnListing(PrincipalsListing):
    slot = 'leftlisting'
    list_columns = PrincipalsListing.user_list_columns
    listing_attrs = PrincipalsListing.user_attrs
    localmanager_ids = PrincipalsListing.user_localmanager_ids
    sort_attr = PrincipalsListing.user_default_sort_column
    css = 'users'
    batchname = 'leftbatch'
    delete_label = _('delete_user', default='Delete User')
    delete_permission = 'delete_user'

    @property
    def current_id(self):
        return self.request.params.get('pid')
