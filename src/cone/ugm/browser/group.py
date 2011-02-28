from plumber import plumber
from yafowil.base import factory
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
    
    @property
    def sortheader(self):
        ret = list()
        for id in ['name', 'surname', 'email']:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': id,
            })
        ret[0]['default'] = True
        return ret
    
    @property
    def items(self):
        ret = list()
        members = self.model.attrs['member']
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
            # XXX: from config
            head = '<span class="sort_name">%s&nbsp;</span>' + \
                   '<span class="sort_surname">%s&nbsp;</span>' + \
                   '<span class="sort_email">&lt;%s&gt;</span>'
            cn = user.attrs.get('cn', '')
            sn = user.attrs.get('sn', '')
            mail = user.attrs.get('mail', '')
            head = head % (cn, sn, mail)
            ret.append({
                'target': item_target,
                'head': head,
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
    
    @property
    def sortheader(self):
        ret = list()
        for id in ['name', 'surname', 'email']:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': id,
            })
        ret[0]['default'] = True
        return ret
    
    @property
    def items(self):
        ret = list()
        members = self.model.attrs['member']
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
            
            # XXX: from config
            head = '<span class="sort_name">%s&nbsp;</span>' + \
                   '<span class="sort_surname">%s&nbsp;</span>' + \
                   '<span class="sort_email">&lt;%s&gt;</span>'
            cn = attrs.get('cn')
            cn = cn and cn[0] or ''
            sn = attrs.get('sn')
            sn = sn and sn[0] or ''
            mail = attrs.get('mail')
            mail = mail and mail[0] or ''
            head = head % (cn, sn, mail)
            ret.append({
                'target': item_target,
                'head': head,
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
        }
        if resource == 'edit':
            props['mode'] = 'display'
        form['name'] = factory(
            'field:label:error:mode:text',
            value=self.model.__name__,
            props=props)
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
        pass
    
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