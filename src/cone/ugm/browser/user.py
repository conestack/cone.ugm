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
from cone.ugm.browser.columns import Column
from cone.ugm.browser.expires import ExpirationForm
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.portrait import PortraitForm
from cone.ugm.browser.principal import PrincipalForm
from cone.ugm.browser.roles import PrincipalRolesForm
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_general
from cone.ugm.model.utils import ugm_users
from plumber import plumber
from pyramid.i18n import TranslationStringFactory
from pyramid.security import has_permission
from webob.exc import HTTPFound
from yafowil.base import ExtractionError
from yafowil.base import UNSET
import copy


_ = TranslationStringFactory('cone.ugm')


@tile('leftcolumn', interface=User, permission='view')
class UserLeftColumn(Column):

    add_label = _('add_user', 'Add User')

    @property
    def can_add(self):
        return has_permission('add_user', self.model.parent, self.request)

    def render(self):
        setattr(self.request, '_curr_listing_id', self.model.name)
        return self._render(self.model.parent, 'leftcolumn')


@tile('rightcolumn', 'templates/right_column.pt',
      interface=User, permission='view')
class UserRightColumn(Tile):

    @property
    def default_widget(self):
        settings = ugm_general(self.model)
        return settings.attrs['default_membership_assignment_widget']


class Groups(object):
    """Descriptor to return principal items for listing

    XXX: check also group.Principals, naming here is sometimes newer
    XXX: speedup!
    """
    def __init__(self,
                 related_only=False,
                 available_only=False):
        self.related_only = related_only
        self.available_only = available_only

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        appuser = obj.model
        user = appuser.model
        groups = user.groups
        related_ids = [g.name for g in groups]

        # always True if we list members only, otherwise will be set
        # in the loop below
        related = self.related_only

        available_only = self.available_only

        if related and available_only:
            raise Exception(u"Invalid object settings.")

        if not related:
            # XXX: LDAP query here.
            groups = obj.model.root['groups'].backend.values()
            if available_only:
                groups = [g for g in groups if not g.name in related_ids]

        # reduce for local manager
        if obj.model.local_manager_consider_for_user:
            local_gids = obj.model.local_manager_target_gids
            groups = [g for g in groups if g.name in local_gids]

        ret = list()

        can_change = has_permission(
            'manage_membership', obj.model.parent, obj.request)

        attrlist = obj.group_attrs
        sort_attr = obj.group_default_sort_column

        # XXX: These should be the mapped attributes - lack of backend support
        for group in groups:
            gid = group.name
            attrs = group.attrs

            # XXX: resource was only set for alluserlisting
            item_target = make_url(obj.request, path=group.path[1:])
            action_query = make_query(id=gid)
            action_target = make_url(obj.request,
                                     node=appuser,
                                     query=action_query)

            if not self.related_only:
                related = gid in related_ids

            actions = list()
            if can_change:
                action_id = 'add_item'
                action_enabled = not bool(related)
                action_title = _('add_user_to_selected_group',
                                 'Add user to selected group')
                add_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(add_item_action)

                action_id = 'remove_item'
                action_enabled = bool(related)
                action_title = _('remove_user_from_selected_group',
                                 'Remove user from selected group')
                remove_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(remove_item_action)

            vals = [obj.extract_raw(attrs, attr) for attr in attrlist]
            sort = obj.extract_raw(attrs, sort_attr)
            content = obj.item_content(*vals)
            current = False
            item = obj.create_item(sort, item_target,
                                   content, current, actions)
            ret.append(item)
        return ret


@tile('columnlisting', 'templates/column_listing.pt',
      interface=User, permission='view')
class GroupsOfUserColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    query_items = Groups(related_only=True)
    batchname = 'rightbatch'


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=User, permission='view')
class AllGroupsColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    query_items = Groups(related_only=False)
    batchname = 'rightbatch'

    @property
    def ajax_action(self):
        return 'allcolumnlisting'


@tile('inoutlisting', 'templates/in_out.pt',
      interface=User, permission='view')
class InOutListing(ColumnListing):
    selected_items = Groups(related_only=True)
    available_items = Groups(available_only=True)

    @property
    def group_attrs(self):
        settings = ugm_general(self.model)
        return [settings.attrs['group_display_name_attr']]

    @property
    def group_default_sort_column(self):
        settings = ugm_general(self.model)
        return settings.attrs['group_display_name_attr']

    @property
    def display_control_buttons(self):
        return True
        #settings = ugm_general(self.model)
        #return settings.attrs['controls_membership_assignment_widget']


class UserForm(PrincipalForm):
    form_name = 'userform'

    @property
    def form_attrmap(self):
        settings = ugm_users(self.model)
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
        config = ugm_users(self.model)
        aliases = config.attrs.users_aliases_attrmap
        return aliases['id'], aliases['login']


@tile('addform', interface=User, permission='add_user')
class UserAddForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = (
        AddBehavior,
        PrincipalRolesForm,
        PortraitForm,
        ExpirationForm,
        AutoIncrementForm,
        AddFormFiddle,
    )

    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = ugm_users(self.model)
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
        password = extracted.pop('userPassword')
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
        # XXX: access already added user after invalidation.
        #      if not done, there's some kind of race condition with ajax
        #      continuation. figure out why.
        self.model.parent[uid]

    def next(self, request):
        next_resource = self.request.environ.get('next_resource')
        if next_resource:
            url = make_url(request.request,
                           node=self.model,
                           resource=next_resource)
        else:
            url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)


@tile('editform', interface=User, permission='edit_user', strict=False)
class UserEditForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = (
        EditBehavior,
        PrincipalRolesForm,
        PortraitForm,
        ExpirationForm,
        EditFormFiddle,
    )

    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = ugm_users(self.model)
        attrmap = settings.attrs.users_form_attrmap
        for key in attrmap:
            if key in ['id', 'login', 'userPassword']:
                continue
            extracted = data.fetch('userform.%s' % key).extracted
            if not extracted:
                if key in self.model.attrs:
                    del self.model.attrs[key]
            else:
                self.model.attrs[key] = extracted
        # set object classes if missing
        ocs = self.model.model.context.attrs['objectClass']
        for oc in settings.attrs.users_object_classes:
            if isinstance(ocs, basestring):
                ocs = [ocs]
            if not oc in ocs:
                ocs.append(oc)
        if ocs != self.model.model.context.attrs['objectClass']:
            self.model.model.context.attrs['objectClass'] = ocs
        password = data.fetch('userform.userPassword').extracted
        self.model.model.context()
        if password is not UNSET:
            uid = self.model.name
            self.model.parent.backend.passwd(uid, None, password)

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
