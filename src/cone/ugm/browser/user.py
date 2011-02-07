from plumber import plumber
from odict import odict
from paste.httpexceptions import HTTPFound
from zodict import AttributedNode
from yafowil.base import (
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
from cone.app.browser.form import (
    Form,
    AddPart,
    EditPart,
)
from cone.ugm.model.interfaces import IUser
from cone.ugm.browser.columns import Column
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing

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

@tile('columnbatch', interface=IUser, permission='view')
class UserColumnBatch(ColumnBatch):
    pass

@tile('columnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class UserColumnListing(ColumnListing):
    
    slot = 'rightlisting'
    
    @property
    def items(self):
        ret = list()
        return ret
#        for i in range(10):
#            item_target = make_url(self.request,
#                                   node=self.model.root['groups'],
#                                   resource=u'group%i' % i)
#            action_query = make_query(id=u'group%i' % i)
#            action_target = make_url(self.request,
#                                     node=self.model.root['users'],
#                                     resource=self.model.__name__,
#                                     query=action_query)
#            ret.append({
#                'target': item_target,
#                'head': 'User in Group - Group %i' % i,
#                'current': False,
#                'actions': [{
#                    'id': 'add_item',
#                    'enabled': False,
#                    'title': 'Add selected User to Group',
#                    'target': action_target},
#                    {'id': 'remove_item',
#                    'enabled': True,
#                    'title': 'Remove selected User from Group',
#                    'target': action_target}]})
#        return ret

@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class AllUserColumnListing(ColumnListing):
    
    slot = 'rightlisting'
    
    @property
    def items(self):
        ret = list()
        for i in range(10):
            item_target = make_url(self.request,
                                   node=self.model.root['groups'],
                                   resource=u'group%i' % i)
            action_query = make_query(id=u'group%i' % i)
            action_target = make_url(self.request,
                                     node=self.model.root['users'],
                                     resource=self.model.__name__,
                                     query=action_query)
            ret.append({
                'target': item_target,
                'head': 'User in Group - Group %i' % i,
                'current': False,
                'actions': [{
                    'id': 'add_item',
                    'enabled': False,
                    'title': 'Add selected User to Group',
                    'target': action_target},
                    {'id': 'remove_item',
                    'enabled': True,
                    'title': 'Remove selected User from Group',
                    'target': action_target}]})
        return ret

class UserForm(object):
    
    @property
    def schema(self):
        # XXX: info from LDAP Schema.
        return {
            'id': {
                'chain': 'field:*ascii:error:label:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'login': {
                'chain': 'field:*ascii:error:label:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'mail': {
                'chain': 'field:error:label:mode:email'},
            'userPassword': {
                'chain': 'field:error:label:password',
                'props': {
                    'minlength': 6,
                    'ascii': True,
                    'strength': 2}}}
    
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
            props={'action': action})
        settings = self.model.root['settings']
        attrmap = settings.attrs.users_form_attrmap
        if not attrmap:
            return form
        schema = self.schema
        required = self._required_fields
        protected = self._protected_fields
        default_chain = 'field:error:label:mode:text'
        for key, val in attrmap.items():
            field = schema.get(key, dict())
            chain = field.get('chain', default_chain)
            props = dict()
            props['label'] = val
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
                    'next': self.next,
                    'label': 'Cancel',
                    'skip': True,
                })
        self.form = form

@tile('addform', interface=IUser, permission="view")
class UserAddForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddPart
    
    def save(self, widget, data):
        settings = self.model.root['settings']
        attrmap = settings.attrs.users_form_attrmap
        user = AttributedNode()
        for key, val in attrmap.items():
            val = data.fetch('userform.%s' % key).extracted
            if not val:
                continue
            user.attrs[key] = val
        users = self.model.__parent__.ldap_users
        id = user.attrs['id']
        self.next_resource = id
        users[id] = user
        users.context()
        password = data.fetch('userform.userPassword').extracted
        if password is not UNSET:
            users.passwd(id, None, password)
    
    def next(self, request):
        if hasattr(self, 'next_resource'):
            url = make_url(request.request,
                           node=self.model,
                           resource=self.next_resource)
        else:
            url = make_url(request.request, node=self.model)
        return HTTPFound(url)


@tile('editform', interface=IUser, permission="view")
class UserEditForm(UserForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart
    
    def save(self, widget, data):
        settings = self.model.root['settings']
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
        return HTTPFound(make_url(request.request, node=self.model))