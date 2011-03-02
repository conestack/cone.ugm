from plumber import plumber
from odict import odict
from node.base import AttributedNode
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
from cone.app.browser.ajax import AjaxAction
from cone.ugm.model.interfaces import IUser
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


@tile('columnbatch', interface=IUser, permission='view')
class UserColumnBatch(ColumnBatch):
    pass


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class GroupsOfUserColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ['name']

    @property
    def items(self):
        ret = list()
        # XXX: error in self.model.model.groups !
        dn = self.model.model.context.__parent__.child_dn(self.model.model.id)
        criteria = {
            'member': dn,
        }
        groups = self.model.root['groups'].ldap_groups
        result = groups.search(criteria=criteria, attrlist=['cn'])
        node = self.model.root['groups']
        for entry in result:
            item_target = make_url(self.request,
                                   node=node,
                                   resource=entry[0])
            action_query = make_query(id=entry[0])
            action_target = make_url(self.request,
                                     node=self.model,
                                     query=action_query)
            attrs = entry[1]
            cn = attrs.get('cn') and attrs.get('cn')[0] or ''
            ret.append({
                'target': item_target,
                'head': self._itemhead(cn),
                'current': self.current_id == entry[0] and True or False,
                'actions': [{
                    'id': 'add_item',
                    'enabled': False,
                    'title': 'Add selected User to Group',
                    'target': action_target},
                    {'id': 'remove_item',
                    'enabled': True,
                    'title': 'Remove selected User from Group',
                    'target': action_target},
                ]
            })
        return ret


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IUser, permission='view')
class AllGroupsColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ['name']

    @property
    def items(self):
        dn = self.model.model.context.__parent__.child_dn(self.model.model.id)
        criteria = {
            'member': dn,
        }
        groups = self.model.root['groups']
        result = groups.ldap_groups.search(criteria=criteria, attrlist=['cn'])
        member_of = [res[0] for res in result]

        ret = list()
        result = groups.ldap_groups.search(attrlist=['cn'])
        for entry in result:
            item_target = make_url(self.request,
                                   node=groups,
                                   resource=entry[0])
            action_query = make_query(id=entry[0])
            action_target = make_url(self.request,
                                     node=self.model,
                                     query=action_query)
            attrs = entry[1]
            already_member = entry[0] in member_of
            cn = attrs.get('cn') and attrs.get('cn')[0] or ''
            ret.append({
                'target': item_target,
                'head': self._itemhead(cn),
                'current': self.current_id == entry[0] and True or False,
                'actions': [{
                    'id': 'add_item',
                    'enabled': not already_member and True or False,
                    'title': 'Add selected User to Group',
                    'target': action_target},
                    {'id': 'remove_item',
                    'enabled': already_member and True or False,
                    'title': 'Remove selected User from Group',
                    'target': action_target},
                ]
            })
        return ret


class UserForm(object):

    @property
    def schema(self):
        # XXX: info from LDAP Schema.
        return {
            'id': {
                'chain': 'field:*ascii:label:error:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'login': {
                'chain': 'field:*ascii:label:error:mode:text',
                'props': {
                    'ascii': True},
                'custom': {
                    'ascii': ([ascii_extractor], [], [], [])}},
            'mail': {
                'chain': 'field:label:error:mode:email'},
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
                'class': 'ajax',
            })
        settings = self.model.root['settings']
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
        if request.get('ajax'):
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)


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
        url = make_url(request.request, node=self.model)
        if request.get('ajax'):
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
