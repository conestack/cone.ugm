from cone.app import compat
from cone.app.browser.ajax import AjaxAction
from cone.app.browser.authoring import ContentAddForm
from cone.app.browser.authoring import ContentEditForm
from cone.app.browser.form import Form
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.app.ugm import ugm_backend
from cone.tile import Tile
from cone.tile import tile
from cone.ugm import events
from cone.ugm.browser.authoring import AddFormFiddle
from cone.ugm.browser.authoring import EditFormFiddle
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.principal import group_field
from cone.ugm.browser.principal import PrincipalForm
from cone.ugm.browser.roles import PrincipalRolesForm
from cone.ugm.model.group import Group
from cone.ugm.utils import general_settings
from odict import odict
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from webob.exc import HTTPFound
from zope.event import notify
import fnmatch
import itertools


_ = TranslationStringFactory('cone.ugm')


@tile(
    name='leftcolumn',
    path='templates/principal_left_column.pt',
    interface=Group,
    permission='view')
class GroupLeftColumn(Tile):

    @property
    def principals_target(self):
        query = make_query(pid=self.model.name)
        return make_url(self.request, node=self.model.parent, query=query)


@tile(
    name='rightcolumn',
    path='templates/principal_right_column.pt',
    interface=Group,
    permission='view')
class GroupRightColumn(Tile):
    pass


class UsersListing(ColumnListing):
    members_only = False

    @property
    def listing_items(self):
        appgroup = self.model
        group = appgroup.model
        member_ids = group.keys()
        # Always True if we list members only, otherwise will be set
        # in the loop below
        related = self.members_only
        # XXX: so far only users as members of groups, for
        # group-in-group we need to prefix groups
        if related:
            users = group.users
        else:
            # XXX: speedup
            users = group.root.users.values()
        # reduce for local manager
        if self.model.local_manager_consider_for_user:
            local_uids = self.model.local_manager_target_uids
            users = [u for u in users if u.name in local_uids]
        attrlist = self.user_attrs
        sort_attr = self.user_default_sort_column
        filter_term = self.unquoted_param_value('filter')
        can_change = self.request.has_permission(
            'manage_membership',
            self.model.parent
        )
        ret = list()
        for user in users:
            attrs = user.attrs
            # reduce by search term
            if filter_term:
                s_attrs = [
                    attrs[attr] for attr in attrlist
                    if attrs[attr] is not None
                ]
                if not fnmatch.filter(s_attrs, filter_term):
                    continue
            uid = user.name
            item_target = make_url(self.request, path=user.path[1:])
            action_query = make_query(id=uid)
            action_target = make_url(
                self.request,
                node=appgroup,
                query=action_query
            )
            if not self.members_only:
                related = uid in member_ids
            actions = list()
            if can_change:
                action_id = 'add_item'
                action_enabled = not bool(related)
                action_title = _(
                    'add_user_to_selected_group',
                    default='Add user to selected group'
                )
                add_item_action = self.create_action(
                    action_id,
                    action_enabled,
                    action_title,
                    action_target
                )
                actions.append(add_item_action)
                action_id = 'remove_item'
                action_enabled = bool(related)
                action_title = _(
                    'remove_user_from_selected_group',
                    default='Remove user from selected group'
                )
                remove_item_action = self.create_action(
                    action_id,
                    action_enabled,
                    action_title,
                    action_target
                )
                actions.append(remove_item_action)
            vals = [self.extract_raw(attrs, attr) for attr in attrlist]
            sort = self.extract_raw(attrs, sort_attr)
            content = self.item_content(*vals)
            current = False
            item = self.create_item(
                sort,
                item_target,
                content,
                current,
                actions
            )
            ret.append(item)
        return ret


@tile(
    name='columnlisting',
    path='templates/column_listing.pt',
    interface=Group,
    permission='view')
class UsersOfGroupColumnListing(UsersListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    members_only = True
    batchname = 'rightbatch'
    display_limit = True
    display_limit_checked = False


@tile(
    name='allcolumnlisting',
    path='templates/column_listing.pt',
    interface=Group,
    permission='view')
class AllUsersColumnListing(UsersListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    batchname = 'rightbatch'
    display_limit = True
    display_limit_checked = True

    @property
    def ajax_action(self):
        return 'allcolumnlisting'


class GroupForm(PrincipalForm):
    form_name = 'groupform'
    field_factory_registry = group_field

    @property
    def reserved_attrs(self):
        return odict([
            ('id', _('group_id', default='Group ID'))
        ])

    @property
    def form_attrmap(self):
        return general_settings(self.model).attrs.groups_form_attrmap


@tile(name='addform', interface=Group, permission="add_group")
@plumbing(ContentAddForm, PrincipalRolesForm, AddFormFiddle)
class GroupAddForm(GroupForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        extracted = dict()
        for attr_name in itertools.chain(self.reserved_attrs, self.form_attrmap):
            value = data[attr_name].extracted
            if not value:
                continue
            extracted[attr_name] = value
        groups = ugm_backend.ugm.groups
        group_id = extracted.pop('id')
        groups.create(group_id, **extracted)
        groups()
        notify(events.GroupCreatedEvent(principal=groups[group_id]))
        self.request.environ['next_resource'] = group_id
        self.model.parent.invalidate()

    def next(self, request):
        next_resource = self.request.environ.get('next_resource')
        if next_resource:
            query = make_query(pid=next_resource)
            url = make_url(request.request, node=self.model.parent, query=query)
        else:
            url = make_url(request.request, node=self.model.parent)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)


@tile(name='editform', interface=Group, permission="edit_group", strict=False)
@plumbing(ContentEditForm, PrincipalRolesForm, EditFormFiddle)
class GroupEditForm(GroupForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        attrs = self.model.attrs
        for attr_name in self.form_attrmap:
            if attr_name in ['id']:
                continue
            attrs[attr_name] = data[attr_name].extracted
        self.model()
        notify(events.GroupModifiedEvent(principal=self.model))

    def next(self, request):
        came_from = request.get('came_from')
        if came_from:
            came_from = compat.unquote(came_from)
            url = '{}?pid={}'.format(came_from, self.model.name)
        else:
            url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
