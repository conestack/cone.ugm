from plumber import plumber
from node.base import AttributedNode
from yafowil.base import factory, ExtractionError
from yafowil.common import ascii_extractor
from yafowil.utils import UNSET
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
from cone.ugm.model.interfaces import IGroup
from cone.ugm.browser.columns import Column
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
        related = self.members_only

        # XXX: so far only users as members of groups, for
        # group-in-group we need to prefix groups
        if self.members_only:
            users = group
        else:
            users = obj.model.root['users'].ldap_users

        col_1_attr, col_2_attr, col_3_attr, sort_attr = obj.user_attrs
        ret = list()
        try:
            attrlist = [col_1_attr, col_2_attr, col_3_attr]
            result = users.search(attrlist=attrlist)
        except Exception, e:
            print 'Query Failed: ' + str(e)
            return []

        # XXX: These should be the mapped attributes - lack of backend support
        for id, attrs in result:
            # XXX: resource was only set for alluserlisting
            try:
                user = users[id]
            except KeyError, e:
                # XXX logging
                print e
                continue

            item_target = make_url(obj.request, node=user, resource=id)
            action_query = make_query(id=id)
            action_target = make_url(obj.request,
                                     node=appgroup,
                                     query=action_query)

            if not self.members_only:
                related = id in member_ids

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
            val_1 = obj.extract_raw(attrs, col_1_attr)
            val_2 = obj.extract_raw(attrs, col_2_attr)
            val_3 = obj.extract_raw(attrs, col_3_attr)
            content = obj.item_content(val_1, val_2, val_3)
            sort = obj.extract_raw(attrs, sort_attr)
            current = False
            item = obj.create_item(sort, item_target, content, current, actions)
            ret.append(item)
        return ret


@tile('columnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class UsersOfGroupColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    query_items = Principals(members_only=True)
    batchname = 'rightbatch'


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=IGroup, permission='view')
class AllUsersColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    query_items = Principals()
    batchname = 'rightbatch'

    @property
    def ajax_action(self):
        return 'allcolumnlisting'


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
            })
        props = {
            'label': 'Name',
            'required': 'No group id defined',
            'ascii': True,
            'html5required': False,
        }
        if resource == 'edit':
            props['mode'] = 'display'
        form['name'] = factory(
            'field:*ascii:*exists:label:error:mode:text',
            value=self.model.__name__,
            props=props,
            custom= {
                'ascii': ([ascii_extractor], [], [], []),
                'exists': ([self.exists], [], [], []),
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

    def exists(self, widget, data):
        group_id = data.extracted
        if group_id is UNSET:
            return data.extracted
        if group_id in self.model.__parent__.ldap_groups:
            msg = "Group %s already exists." % (group_id,)
            raise ExtractionError(msg)
        return data.extracted

@tile('addform', interface=IGroup, permission="add")
class GroupAddForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddPart

    def save(self, widget, data):
        group = AttributedNode()
        id = data.fetch('groupform.name').extracted
        groups = self.model.__parent__.ldap_groups
        self.request.environ['next_resource'] = id
        groups[id] = group
        groups.context()
        self.model.__parent__.invalidate()

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


@tile('editform', interface=IGroup, permission="edit")
class GroupEditForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart

    def save(self, widget, data):
        pass

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
