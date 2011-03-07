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


class Principals(object):
    """Descriptor to return principal items for listing
    """
    def __init__(self, members_only=False):
        self.members_only = members_only

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        appgroup = obj.model
        group = appgroup.model
        member_ids = group.keys()
        # always True if we list members only, otherwise will be set
        # in the loop below
        already_member = self.members_only

        # XXX: so far only users as members of groups, for
        # group-in-group we need to prefix groups
        if self.members_only:
            users = group
        else:
            users = obj.model.root['users'].ldap_users

        ret = list()

        # XXX: These should be the mapped attributes - lack of backend support
        for id, attrs in users.search(attrlist=('cn', 'sn', 'mail')):
            # XXX: resource was only set for alluserlisting
            item_target = make_url(obj.request, node=users[id], resource=id)
            action_query = make_query(id=id)
            action_target = make_url(obj.request, node=appgroup, query=action_query)

            if not self.members_only:
                already_member = id in member_ids

            # XXX: this should not be hardcoded
            cn = attrs.get('cn', '')
            sn = attrs.get('sn', '')
            mail = attrs.get('mail', '')
            ret.append({
                'target': item_target,
                'head': obj._itemhead(cn, sn, mail),
                'current': False,
                'actions': [
                    {
                        'id': 'add_item',
                        'enabled': not bool(already_member),
                        'title': 'Add user to selected group.',
                        'target': action_target,
                    },
                    {
                        'id': 'remove_item',
                        'enabled': bool(already_member),
                        'title': 'Remove user from selected group.',
                        'target': action_target,
                    },
                ],
            })
        return ret


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class UsersOfGroupColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ['name', 'surname', 'email']
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    items = Principals(members_only=True)


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class AllUsersColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ['name', 'surname', 'email']
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    items = Principals()


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
