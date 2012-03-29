import copy
from plumber import plumber
from pyramid.security import has_permission
from yafowil.base import (
    ExtractionError,
    UNSET,
)
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.app.browser.form import Form
from cone.app.browser.authoring import (
    AddPart,
    EditPart,
)
from cone.app.browser.ajax import AjaxAction
from cone.ugm.model.user import User
from cone.ugm.model.utils import (
    ugm_general,
    ugm_users,
)
from cone.ugm.browser import form_field_definitions
from cone.ugm.browser.columns import Column
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.roles import PrincipalRolesForm
from cone.ugm.browser.authoring import (
    AddFormFiddle,
    EditFormFiddle,
)
from cone.ugm.browser.principal import PrincipalForm
from cone.ugm.browser.expires import ExpirationForm
from cone.ugm.browser.autoincrement import AutoIncrementForm
from webob.exc import HTTPFound


@tile('leftcolumn', interface=User, permission='view')
class UserLeftColumn(Column):

    add_label = u"Add User"
    
    @property
    def can_add(self):
        return has_permission('add', self.model.parent, self.request)

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
        
        ret = list()
        
        can_change = has_permission(
            'manage_membership', obj.model.parent, obj.request)
        
        attrlist = obj.group_attrs
        sort_attr = obj.group_default_sort_column

        # XXX: These should be the mapped attributes - lack of backend support
        for group in groups:
            id = group.name
            attrs = group.attrs

            # XXX: resource was only set for alluserlisting
            item_target = make_url(obj.request, path=group.path[1:])
            action_query = make_query(id=id)
            action_target = make_url(obj.request,
                                     node=appuser,
                                     query=action_query)

            if not self.related_only:
                related = id in related_ids

            actions = list()
            if can_change:
                action_id = 'add_item'
                action_enabled = not bool(related)
                action_title = 'Add user to selected group'
                add_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(add_item_action)

                action_id = 'remove_item'
                action_enabled = bool(related)
                action_title = 'Remove user from selected group'
                remove_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(remove_item_action)
            
            vals = [obj.extract_raw(attrs, attr) for attr in attrlist]
            sort = obj.extract_raw(attrs, sort_attr)
            content = obj.item_content(*vals)
            current = False
            item = obj.create_item(sort, item_target, content, current, actions)
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
        id, login = self._get_auth_attrs()
        if id != login:
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
        id = data.extracted
        if id is UNSET:
            return data.extracted
        if id in self.model.parent.backend:
            msg = "User %s already exists." % (id,)
            raise ExtractionError(msg)
        return data.extracted
    
    def optional_login(self, widget, data):
        id, login = self._get_auth_attrs()
        res = self.model.parent.backend.search(criteria={login: data.extracted})
        # no entries found with same login attribute set.
        if not res:
            return data.extracted
        # 1-lenght result, unchange login attribute
        if len(res) == 1:
            if res[0] == self.model.name:
                return data.extracted
        msg = "User login %s not unique." % data.extracted
        raise ExtractionError(msg)
    
    def _get_auth_attrs(self):
        config = ugm_users(self.model)
        aliases = config.attrs.users_aliases_attrmap
        return aliases['id'], aliases['login']


@tile('addform', interface=User, permission='add')
class UserAddForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = (
        AddPart,
        PrincipalRolesForm,
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
        users = self.model.parent.backend
        id = extracted.pop('id')
        password = extracted.pop('userPassword')
        users.create(id, **extracted)
        self.request.environ['next_resource'] = id
        users()
        if password is not UNSET:
            users.passwd(id, None, password)
        self.model.parent.invalidate()
        # XXX: access already added user after invalidation.
        #      if not done, there's some kind of race condition with ajax
        #      continuation. figure out why.
        self.model.parent[id]

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


@tile('editform', interface=User, permission='edit', strict=False)
class UserEditForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = (
        EditPart,
        PrincipalRolesForm,
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
        
        password = data.fetch('userform.userPassword').extracted
        self.model.model.context()
        if password is not UNSET:
            id = self.model.name
            self.model.parent.backend.passwd(id, None, password)

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)