from plumber import plumber
from node.base import AttributedNode
from yafowil.base import factory
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
from cone.ugm.model.interfaces import IGroup
from cone.ugm.browser.columns import Column
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing
from webob.exc import HTTPFound


@tile('leftcolumn', interface=IGroup, permission='view')
class GroupLeftColumn(Column):

    add_label = u"Add Group"

    def render(self):
        self.request['_curr_listing_id'] = self.model.__name__
        return self._render(self.model.__parent__, 'leftcolumn')


@tile('rightcolumn', 'templates/right_column.pt',
      interface=IGroup, permission='view')
class GroupRightColumn(Tile):
    pass


@tile('columnbatch', interface=IGroup, permission='view')
class GroupColumnBatch(ColumnBatch):
    pass


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class UsersOfGroupColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ['name', 'surname', 'email']

    @property
    def items(self):
        ret = list()
        members = self.model.attrs['uniqueMember']
        users = self.model.root['users']
        for member in members:
            try:
                id = users.ldap_users.idbydn(member)
            except KeyError:
                continue
            user = users[id]
            item_target = make_url(self.request,
                                   node=user)
            action_query = make_query(id=id)
            action_target = make_url(self.request,
                                     node=self.model,
                                     query=action_query)
            cn = user.attrs.get('cn', '')
            sn = user.attrs.get('sn', '')
            mail = user.attrs.get('mail', '')
            ret.append({
                'target': item_target,
                'head': self._itemhead(cn, sn, mail),
                'current': False,
                'actions': [
                    {
                        'id': 'add_item',
                        'enabled': False,
                        'title': 'Add User to selected Group',
                        'target': action_target,
                    },
                    {
                        'id': 'remove_item',
                        'enabled': True,
                        'title': 'Remove User from selected Group',
                        'target': action_target,
                    },
                ],
            })
        return ret


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class AllUsersColumnListing(ColumnListing):

    slot = 'rightlisting'
    list_columns = ['name', 'surname', 'email']

    @property
    def items(self):
        ret = list()
        members = self.model.attrs['uniqueMember']
        users = self.model.root['users']
        member_ids = list()
        for member in members:
            try:
                member_ids.append(users.ldap_users.idbydn(member))
            except KeyError:
                continue
        result = users.ldap_users.search(criteria=None,
                                         attrlist=['cn', 'sn' , 'mail'])
        for entry in result:
            item_target = make_url(self.request,
                                   node=users,
                                   resource=entry[0])
            action_query = make_query(id=entry[0])
            action_target = make_url(self.request,
                                     node=self.model,
                                     query=action_query)
            attrs = entry[1]
            already_member = entry[0] in member_ids

            cn = attrs.get('cn') and attrs.get('cn')[0] or ''
            sn = attrs.get('sn') and attrs.get('sn')[0] or ''
            mail = attrs.get('mail') and attrs.get('mail')[0] or ''
            ret.append({
                'target': item_target,
                'head': self._itemhead(cn, sn, mail),
                'current': False,
                'actions': [
                    {
                        'id': 'add_item',
                        'enabled': not already_member and True or False,
                        'title': 'Add User to selected Group',
                        'target': action_target,
                    },
                    {
                        'id': 'remove_item',
                        'enabled': already_member and True or False,
                        'title': 'Remove User from selected Group',
                        'target': action_target,
                    },
                ],
            })
        return ret


class GroupForm(object):

    def prepare(self):
        resource = 'add'
        if self.model.__name__ is not None:
            resource = 'edit'
        action = make_url(self.request, node=self.model, resource=resource)
        form = factory(
            u'form',
            name='groupform',
            props={
                'action': action,
                'class': 'ajax',
            })
        props = {
            'label': 'Name',
            'required': 'No group id defined',
            'ascii': True,
        }
        if resource == 'edit':
            props['mode'] = 'display'
        form['name'] = factory(
            'field:*ascii:label:error:mode:text',
            value=self.model.__name__,
            props=props,
            custom= {
                'ascii': ([ascii_extractor], [], [], []),
            })
        if resource =='add': # XXX: no fields to edit atm
            form['save'] = factory(
                'submit',
                props={
                    'action': 'save',
                    'expression': True,
                    'handler': self.save,
                    'next': self.next,
                    'label': 'Save',
                })
        if resource =='add':
            form['cancel'] = factory(
                'submit',
                props={
                    'action': 'cancel',
                    'expression': True,
                    'next': self.next,
                    'label': 'Cancel',
                    'skip': True,
                })
        self.form = form


@tile('addform', interface=IGroup, permission="view")
class GroupAddForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddPart

    def save(self, widget, data):
        group = AttributedNode()
        group.attrs['cn'] = data.fetch('groupform.name').extracted
        group.attrs['uniqueMember'] = ['cn=nobody']
        groups = self.model.__parent__.ldap_groups
        cn = group.attrs['cn']
        self.next_resource = cn
        groups[cn] = group
        groups.context()

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


@tile('editform', interface=IGroup, permission="view")
class GroupEditForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart

    def save(self, widget, data):
        pass

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if request.get('ajax'):
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
