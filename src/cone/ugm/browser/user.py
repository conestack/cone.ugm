from plumber import plumber
from odict import odict
from yafowil.base import (
    ExtractionError,
    factory,
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
from cone.ugm import form_field_definitions
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_users
from cone.ugm.browser.columns import Column
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing
from cone.ugm.browser.authoring import (
    AddFormFiddle,
    EditFormFiddle,
)
from webob.exc import HTTPFound


@tile('leftcolumn', interface=User, permission='view')
class UserLeftColumn(Column):

    add_label = u"Add User"

    def render(self):
        setattr(self.request, '_curr_listing_id', self.model.name)
        return self._render(self.model.parent, 'leftcolumn')


@tile('rightcolumn', 'templates/right_column.pt',
      interface=User, permission='view')
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
        groups = user.groups
        related_ids = [g.name for g in groups]
        
        # always True if we list members only, otherwise will be set
        # in the loop below
        related = self.related_only

        if not self.related_only:
            groups = obj.model.root['groups'].backend.values()

        ret = list()
        
        # XXX
        col_1_attr = obj.group_attrs

        # XXX: These should be the mapped attributes - lack of backend support
        for group in groups:
            id = group.name

            # XXX: resource was only set for alluserlisting
            # XXX: path instead of node=user, (ugm)
            item_target = make_url(obj.request, path=group.path[1:])
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

from yafowil.common import ascii_extractor

class UserForm(object):

    @property
    def schema(self):
        # XXX: get info from config...
        return {
            'id': {
                'chain': 'field:*ascii:*exists:label:error:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], []),
                    'exists': ([self.exists], [], [], [])
                    },
                },
            'login': {
                'chain': 'field:*ascii:label:error:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'mail': {
                'chain': 'field:label:error:email',
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
        # XXX: get info from config...
        return ['id', 'login']

    @property
    def _required_fields(self):
        # XXX: get info from config...
        return ['id', 'login', 'cn', 'sn', 'mail', 'userPassword']

    def prepare(self):
        resource = self.action_resource
        # XXX: tmp - load props each time they are accessed.
        if resource == 'edit':
            self.model.attrs.context.load()
        action = make_url(self.request, node=self.model, resource=resource)
        # create user form
        form = factory(
            u'form',
            name='userform',
            props={
                'action': action,
            })
        settings = ugm_users(self.model)
        attrmap = settings.attrs.users_form_attrmap
        if not attrmap:
            return form
        
        # XXX: later
        
#        schema = form_field_definitions.user
#        default = form_field_definitions.user['default']
#        for key, val in attrmap.items():
#            field = schema.get(key, default)
#            chain = field['chain']
#            props = dict()
#            props['label'] = val
#            if field.get('required'):
#                props['required'] = 'No %s defined' % val
#            props.update(field.get('props', dict()))
#            value = UNSET
#            mode = 'edit'
#            if resource == 'edit':
#                if field.get('protected'):
#                    mode = 'display'
#                value = self.model.attrs.get(key, u'')
#            
#            custom = field.get('custom', dict())
#            custom_parsed = dict()
#            if custom.keys():
#                for key, val in custom.items():
#                    val_parsed = list()
#                    for chain in val:
#                        chain_parsed = list()
#                        for part in chain:
#                            if isinstance(part, basestring):
#                                if not part.startswith('context.'):
#                                    raise Exception(
#                                        u"chain callable definition invalid")
#                                attrname = part[part.index('.') + 1:]
#                                callable = getattr(self, attrname)
#                            else:
#                                callable = part
#                            chain_parsed.append(callable)
#                        val_parsed.append(chain_parsed)
#                    custom_parsed[key] = tuple(val_parsed)
#            
#            import pdb;pdb.set_trace()
#            
#            form[key] = factory(
#                chain,
#                value=value,
#                props=props,
#                custom=custom_parsed,
#                mode=mode)

        schema = self.schema
        required = self._required_fields
        protected = self._protected_fields
        default_chain = 'field:label:error:text'
        for key, val in attrmap.items():
            field = schema.get(key, dict())
            chain = field.get('chain', default_chain)
            props = dict()
            props['label'] = val
            if key in required:
                props['required'] = 'No %s defined' % val
            props.update(field.get('props', dict()))
            value = UNSET
            mode = 'edit'
            if resource == 'edit':
                if key in protected:
                    mode = 'display'
                value = self.model.attrs.get(key, u'')
            form[key] = factory(
                chain,
                value=value,
                props=props,
                custom=field.get('custom', dict()),
                mode=mode)

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
        if id in self.model.parent.backend:
            msg = "User %s already exists." % (id,)
            raise ExtractionError(msg)
        return data.extracted


@tile('addform', interface=User, permission='add')
class UserAddForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddPart, AddFormFiddle
    
    show_heading = False

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
        user = users.create(id, **extracted)
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


@tile('editform', interface=User, permission='edit')
class UserEditForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart, EditFormFiddle
    
    show_heading = False

    def save(self, widget, data):
        settings = ugm_users(self.model)
        attrmap = settings.attrs.users_form_attrmap
        for key, val in attrmap.items():
            if key in ['id', 'login', 'userPassword']:
                continue
            extracted = data.fetch('userform.%s' % key).extracted
            self.model.attrs[key] = extracted
        self.model.model.context()
        password = data.fetch('userform.userPassword').extracted
        if password is not UNSET:
            id = self.model.name
            self.model.parent.ldap_users.passwd(id, None, password)

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
