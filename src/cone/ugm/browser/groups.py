from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.tile import Tile
from cone.tile import tile
from cone.ugm.browser.columns import Column
from cone.ugm.browser.listing import PrincipalsListing
from cone.ugm.model.groups import Groups
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@tile(
    name='leftcolumn',
    path='templates/principals_left_column.pt',
    interface=Groups,
    permission='view')
class GroupsLeftColumn(Tile):
    add_label = _('add_group', default='Add Group')

    @property
    def add_target(self):
        return make_url(
            self.request,
            node=self.model.root['groups'],
            query=make_query(factory=u'group')
        )

    @property
    def can_add(self):
        return self.request.has_permission('add_group', self.model)


@tile(
    name='rightcolumn',
    path='templates/principals_right_column.pt',
    interface=Groups,
    permission='view')
class GroupsRightColumn(Column):

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
    interface=Groups,
    permission='view')
class GroupsColumnListing(PrincipalsListing):
    slot = 'leftlisting'
    list_columns = PrincipalsListing.group_list_columns
    listing_attrs = PrincipalsListing.group_attrs
    localmanager_ids = PrincipalsListing.group_localmanager_ids
    sort_attr = PrincipalsListing.group_default_sort_column
    css = 'groups'
    batchname = 'leftbatch'
    delete_label = _('delete_group', default='Delete Group')
    delete_permission = 'delete_group'

    @property
    def current_id(self):
        return self.request.params.get('pid')
