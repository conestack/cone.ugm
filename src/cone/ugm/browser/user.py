from cone.app import compat
from cone.app.browser.ajax import AjaxAction
from cone.app.browser.authoring import AddBehavior
from cone.app.browser.authoring import EditBehavior
from cone.app.browser.form import Form
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.tile import Tile
from cone.tile import tile
from cone.ugm.browser import form_field_definitions
from cone.ugm.browser.authoring import AddFormFiddle
from cone.ugm.browser.authoring import EditFormFiddle
from cone.ugm.browser.autoincrement import AutoIncrementForm
from cone.ugm.browser.expires import ExpirationForm
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.portrait import PortraitForm
from cone.ugm.browser.principal import PrincipalForm
from cone.ugm.browser.roles import PrincipalRolesForm
from cone.ugm.model.user import User
from cone.ugm.utils import general_settings
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from webob.exc import HTTPFound
from yafowil.base import ExtractionError
from yafowil.base import UNSET
import copy
import fnmatch


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
                s_attrs = [attrs[attr] for attr in attrlist]
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

    @property
    def form_attrmap(self):
        settings = general_settings(self.model)
        return settings.attrs.users_form_attrmap

    @property
    def form_field_definitions(self):
        """Hook optional_login extractor if necessary for form defaults.
        """
        schema = copy.deepcopy(form_field_definitions.user)
        uid, login = self._get_auth_attrs()
        if uid != login:
            field = schema.get(login, schema['default'])
            if field['chain'].find('*optional_login') == -1:
                field['chain'] = '%s:%s' % (
                    '*optional_login', field['chain'])
                if not field.get('custom'):
                    field['custom'] = dict()
                field['custom']['optional_login'] = \
                    (['context.optional_login'], [], [], [], [])
            schema[login] = field
        return schema

    def exists(self, widget, data):
        uid = data.extracted
        if uid is UNSET:
            return data.extracted
        if uid in self.model.parent.backend:
            message = _('user_already_exists',
                        default="User ${uid} already exists.",
                        mapping={'uid': uid})
            raise ExtractionError(message)
        return data.extracted

    def optional_login(self, widget, data):
        login = self._get_auth_attrs()[1]
        res = self.model.parent.backend.search(
            criteria={login: data.extracted})
        # no entries found with same login attribute set.
        if not res:
            return data.extracted
        # 1-lenght result, unchange login attribute
        if len(res) == 1:
            if res[0] == self.model.name:
                return data.extracted
        message = _('user_login_not_unique',
                    default="User login ${login} not unique.",
                    mapping={'login': data.extracted})
        raise ExtractionError(message)

    def _get_auth_attrs(self):
        settings = general_settings(self.model)
        aliases = settings.attrs.users_reserved_attrs
        return aliases['id'], aliases['login']


@tile(name='addform', interface=User, permission='add_user')
@plumbing(
    AddBehavior,
    PrincipalRolesForm,
    PortraitForm,
    ExpirationForm,
    AutoIncrementForm,
    AddFormFiddle)
class UserAddForm(UserForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = general_settings(self.model)
        attrmap = settings.attrs.users_form_attrmap
        extracted = dict()
        for key, val in attrmap.items():
            val = data.fetch('userform.%s' % key).extracted
            if not val:
                continue
            extracted[key] = val
        # possibly extracted by other behaviors
        # XXX: call next at the end in all extension behaviors to reduce
        #      database queries.
        for key, val in self.model.attrs.items():
            extracted[key] = val
        users = self.model.parent.backend
        uid = extracted.pop('id')
        password = extracted.pop('password')
        users.create(uid, **extracted)
        users()
        if self.model.local_manager_consider_for_user:
            groups = users.parent.groups
            for gid in self.model.local_manager_default_gids:
                groups[gid].add(uid)
            groups()
        self.request.environ['next_resource'] = uid
        if password is not UNSET:
            users.passwd(uid, None, password)
        self.model.parent.invalidate()
        # Access already added user after invalidation. If not done, there's
        # some kind of race condition with ajax continuation.
        # XXX: figure out why.
        self.model.parent[uid]

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
    EditBehavior,
    PrincipalRolesForm,
    PortraitForm,
    ExpirationForm,
    EditFormFiddle)
class UserEditForm(UserForm, Form):
    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = general_settings(self.model)
        attrmap = settings.attrs.users_form_attrmap
        for key in attrmap:
            if key in ['id', 'login', 'password']:
                continue
            extracted = data.fetch('userform.%s' % key).extracted
            if not extracted:
                if key in self.model.attrs:
                    del self.model.attrs[key]
            else:
                self.model.attrs[key] = extracted
        # set object classes if missing
        # XXX: move to cone.ldap
        ocs = self.model.model.context.attrs['objectClass']
        ldap_settings = self.model.root['settings']['ldap_users']
        for oc in ldap_settings.attrs.users_object_classes:
            if isinstance(ocs, compat.STR_TYPE):
                ocs = [ocs]
            if oc not in ocs:
                ocs.append(oc)
        if ocs != self.model.model.context.attrs['objectClass']:
            self.model.model.context.attrs['objectClass'] = ocs
        password = data.fetch('userform.password').extracted
        self.model.model.context()
        if password is not UNSET:
            uid = self.model.name
            self.model.parent.backend.passwd(uid, None, password)

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
