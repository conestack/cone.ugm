from plumber import plumber
from odict import odict
from node.base import AttributedNode
from yafowil.base import (
    ExtractionError,
    factory,
    UNSET,
)
from yafowil.common import ascii_extractor
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
from cone.ugm.model.interfaces import IUser
from cone.ugm.model.utils import ugm_settings
from cone.ugm.browser.columns import Column
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing
from webob.exc import HTTPFound


@tile('leftcolumn', interface=IUser, permission='view')
class UserLeftColumn(Column):

    add_label = u"Add User"

    def render(self):
        self.request['_curr_listing_id'] = self.model.__name__
        return self._render(self.model.__parent__, 'leftcolumn')


@tile('rightcolumn', 'templates/right_column.pt',
      interface=IUser, permission='view')
class UserRightColumn(Tile):
    pass


class Groups(object):
    """Descriptor to return principal items for listing

    XXX: check also group.Principals, naming here is sometimes newer
    """
    def __init__(self, related_only=False):
        self.related_only = related_only

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        appuser = obj.model
        user = appuser.model
        related_ids = user.membership.keys()
        # always True if we list members only, otherwise will be set
        # in the loop below
        related = self.related_only

        if self.related_only:
            groups = user.membership
        else:
            groups = obj.model.root['groups'].ldap_groups

        ret = list()
        col_1_attr = obj.group_attrs
        
        # XXX: These should be the mapped attributes - lack of backend support
        for id in groups.keys():
            group = groups[id]
            
            # XXX: resource was only set for alluserlisting
            item_target = make_url(obj.request, node=group, resource=id)
            action_query = make_query(id=id)
            action_target = make_url(obj.request,
                                     node=appuser,
                                     query=action_query)

            if not self.related_only:
                related = id in related_ids
            
            action_id = 'add_item'
            action_enabled = not bool(related)
            action_title = 'Add user to selected group'
            add_item_action = obj.create_action(
                action_id, action_enabled, action_title, action_target)
            
            action_id = 'remove_item'
            action_enabled = bool(related)
            action_title = 'Remove user from selected group'
            remove_item_action = obj.create_action(
                action_id, action_enabled, action_title, action_target)
            
            actions = [add_item_action, remove_item_action]
            val_1 = group.attrs[col_1_attr]
            content = obj.item_content(val_1)
            item = obj.create_item(val_1, item_target, content, False, actions)
            ret.append(item)
        return ret


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class GroupsOfUserColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    query_items = Groups(related_only=True)
    batchname = 'rightbatch'


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class AllGroupsColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ColumnListing.group_list_columns
    css = 'groups'
    query_items = Groups(related_only=False)
    batchname = 'rightbatch'
    
    @property
    def ajax_action(self):
        return 'allcolumnlisting'


class UserForm(object):

    @property
    def schema(self):
        # XXX: info from LDAP Schema.
        return {
            'id': {
                'chain': 'field:*ascii:*exists:label:error:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], []),
                    'exists': ([self.exists], [], [], [])
                    },
                },
            'login': {
                'chain': 'field:*ascii:label:error:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'mail': {
                'chain': 'field:label:error:mode:email',
                'props': {
                    'html5type': False,
                }},
            'userPassword': {
                'chain': 'field:label:error:password',
                'props': {
                    'minlength': 6,
                    'ascii': True}}}

    @property
    def _protected_fields(self):
        return ['id', 'login']

    @property
    def _required_fields(self):
        return ['id', 'login', 'cn', 'sn', 'mail', 'userPassword']

    def prepare(self):
        resource = 'add'
        if self.model.__name__ is not None:
            resource = 'edit'

            # XXX: tmp - load props each time they are accessed.
            self.model.attrs.context.load()

        action = make_url(self.request, node=self.model, resource=resource)
        form = factory(
            u'form',
            name='userform',
            props={
                'action': action,
            })
        settings = ugm_settings(self.model)
        attrmap = settings.attrs.users_form_attrmap
        if not attrmap:
            return form
        schema = self.schema
        required = self._required_fields
        protected = self._protected_fields
        default_chain = 'field:label:error:mode:text'
        for key, val in attrmap.items():
            field = schema.get(key, dict())
            chain = field.get('chain', default_chain)
            props = dict()
            props['label'] = val
            props['html5required'] = False
            if key in required:
                props['required'] = 'No %s defined' % val
            props.update(field.get('props', dict()))
            value = UNSET
            if resource == 'edit':
                if key in protected:
                    props['mode'] = 'display'
                value = self.model.attrs.get(key, u'')
            form[key] = factory(
                chain,
                value=value,
                props=props,
                custom=field.get('custom', dict()))
        form['save'] = factory(
            'submit',
            props = {
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
                'label': 'Save',
            })
        if resource =='add':
            form['cancel'] = factory(
                'submit',
                props = {
                    'action': 'cancel',
                    'expression': True,
                    'handler': None,
                    'next': self.next,
                    'label': 'Cancel',
                    'skip': True,
                })
        self.form = form

    def exists(self, widget, data):
        id = data.extracted
        if id is UNSET:
            return data.extracted
        if id in self.model.__parent__.ldap_users:
            msg = "User %s already exists." % (id,)
            raise ExtractionError(msg)
        return data.extracted


@tile('addform', interface=IUser, permission='add')
class UserAddForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddPart

    def save(self, widget, data):
        settings = ugm_settings(self.model)
        attrmap = settings.attrs.users_form_attrmap
        user = AttributedNode()
        for key, val in attrmap.items():
            val = data.fetch('userform.%s' % key).extracted
            if not val:
                continue
            user.attrs[key] = val
        users = self.model.__parent__.ldap_users
        id = user.attrs['id']
        self.request.environ['next_resource'] = id
        users[id] = user
        users.context()
        self.model.__parent__.invalidate()
        password = data.fetch('userform.userPassword').extracted
        if password is not UNSET:
            users.passwd(id, None, password)

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


@tile('editform', interface=IUser, permission='edit')
class UserEditForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart

    def save(self, widget, data):
        settings = ugm_settings(self.model)
        attrmap = settings.attrs.users_form_attrmap
        for key, val in attrmap.items():
            if key in ['id', 'login', 'userPassword']:
                continue
            extracted = data.fetch('userform.%s' % key).extracted
            self.model.attrs[key] = extracted
        self.model.model.context()
        password = data.fetch('userform.userPassword').extracted
        if password is not UNSET:
            id = self.model.__name__
            self.model.__parent__.ldap_users.passwd(id, None, password)

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
