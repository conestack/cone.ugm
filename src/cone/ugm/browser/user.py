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
from cone.ugm.browser.autoincrement import AutoIncrementForm
from cone.ugm.browser.expires import ExpirationForm
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.portrait import PortraitForm
from cone.ugm.browser.principal import PrincipalForm
from cone.ugm.browser.principal import user_field
from cone.ugm.browser.roles import PrincipalRolesForm
from cone.ugm.model.user import User
from cone.ugm.utils import general_settings
from odict import odict
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from webob.exc import HTTPFound
from yafowil.base import UNSET
from zope.event import notify
import fnmatch
import itertools


_ = TranslationStringFactory('cone.ugm')


@tile(
    name='leftcolumn',
    path='templates/principal_left_column.pt',
    interface=User,
    permission='view')
class UserLeftColumn(Tile):

    @property
    def principals_target(self):
        query = make_query(pid=self.model.name)
        return make_url(self.request, node=self.model.parent, query=query)


@tile(
    name='rightcolumn',
    path='templates/principal_right_column.pt',
    interface=User,
    permission='view')
class UserRightColumn(Tile):
    pass


class GroupsListing(ColumnListing):
    related_only = False

    @property
    def listing_items(self):
        appuser = self.model
        user = appuser.model
        groups = user.groups
        related_ids = [g.name for g in groups]
        # Always True if we list members only, otherwise will be set
        # in the loop below
        related = self.related_only
        if not related:
            groups = self.model.root['groups'].backend.values()
        # reduce for local manager
        if self.model.local_manager_consider_for_user:
            local_gids = self.model.local_manager_target_gids
            groups = [g for g in groups if g.name in local_gids]
        attrlist = self.group_attrs
        sort_attr = self.group_default_sort_column
        filter_term = self.unquoted_param_value('filter')
        can_change = self.request.has_permission(
            'manage_membership',
            self.model.parent
        )
        ret = list()
        for group in groups:
            attrs = group.attrs
            # reduce by search term
            if filter_term:
                s_attrs = [
                    attrs[attr] for attr in attrlist
                    if attrs[attr] is not None
                ]
                if not fnmatch.filter(s_attrs, filter_term):
                    continue
            gid = group.name
            item_target = make_url(self.request, path=group.path[1:])
            action_query = make_query(id=gid)
            action_target = make_url(
                self.request,
                node=appuser,
                query=action_query
            )
            if not self.related_only:
                related = gid in related_ids
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
    interface=User,
    permission='view')
class GroupsOfUserColumnListing(GroupsListing):
    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    related_only = True
    batchname = 'rightbatch'
    display_limit = True
    display_limit_checked = False


@tile(
    name='allcolumnlisting',
    path='templates/column_listing.pt',
    interface=User,
    permission='view')
class AllGroupsColumnListing(GroupsListing):
    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    batchname = 'rightbatch'
    display_limit = True
    display_limit_checked = True

    @property
    def ajax_action(self):
        return 'allcolumnlisting'


class UserForm(PrincipalForm):
    form_name = 'userform'
    field_factory_registry = user_field

    @property
    def reserved_attrs(self):
        return odict([
            ('id', _('user_id', default='User ID')),
            ('login', _('login_name', default='Login name')),
            ('password', _('password', default='Password'))
        ])

    @property
    def form_attrmap(self):
        return general_settings(self.model).attrs.users_form_attrmap


@tile(name='addform', interface=User, permission='add_user')
@plumbing(
    ContentAddForm,
    PrincipalRolesForm,
    PortraitForm,
    ExpirationForm,
    AutoIncrementForm,
    AddFormFiddle)
class UserAddForm(UserForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        extracted = dict()
        for attr_name in itertools.chain(self.reserved_attrs, self.form_attrmap):
            value = data[attr_name].extracted
            if not value:
                continue
            extracted[attr_name] = value
        # possible values extracted by other user form behaviors
        extracted.update(self.model.attrs)
        users = ugm_backend.ugm.users
        user_id = extracted.pop('id')
        password = extracted.pop('password')
        login_name = general_settings(self.model).attrs.users_login_name_attr
        if login_name:
            extracted[login_name] = extracted.pop('login')
        user = users.create(user_id, **extracted)
        users()
        if self.model.local_manager_consider_for_user:
            groups = ugm_backend.ugm.groups
            for gid in self.model.local_manager_default_gids:
                groups[gid].add(user_id)
            groups()
        self.request.environ['next_resource'] = user_id
        if password is not UNSET:
            users.passwd(user_id, None, password)
        notify(events.UserCreatedEvent(
            principal=user,
            password=password
        ))
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


@tile(name='editform', interface=User, permission='edit_user', strict=False)
@plumbing(
    ContentEditForm,
    PrincipalRolesForm,
    PortraitForm,
    ExpirationForm,
    EditFormFiddle)
class UserEditForm(UserForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        attrs = self.model.attrs
        for attr_name in self.form_attrmap:
            if attr_name in ['id', 'password']:
                continue
            attrs[attr_name] = data[attr_name].extracted
        self.model()
        password = data.fetch('userform.password').extracted
        if password is not UNSET:
            user_id = self.model.name
            ugm_backend.ugm.users.passwd(user_id, None, password)
        notify(events.UserModifiedEvent(
            principal=self.model,
            password=password
        ))

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
