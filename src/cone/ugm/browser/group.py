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
from cone.ugm.model.interfaces import IGroup
from cone.ugm.browser.columns import Column
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.browser.listing import ColumnListing


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
        for id in ['name']:
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
        for i in range(10):
            item_target = make_url(self.request,
                                   node=self.model.root['users'],
                                   resource=u'user%i' % i)
            action_query = make_query(id=u'user%i' % i)
            action_target = make_url(self.request,
                                     node=self.model.root['groups'],
                                     resource=self.model.__name__,
                                     query=action_query)
            
            ret.append({
                'target': item_target,
                'head': 'Group Member - User %i' % i,
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
        for id in ['name']:
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
        for i in range(10):
            item_target = make_url(self.request,
                                   node=self.model.root['users'],
                                   resource=u'user%i' % i)
            action_query = make_query(id=u'user%i' % i)
            action_target = make_url(self.request,
                                     node=self.model.root['groups'],
                                     resource=self.model.__name__,
                                     query=action_query)
            
            ret.append({
                'target': item_target,
                'head': 'Group Member - User %i' % i,
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


class GroupForm(object):
    
    def prepare(self):
        form = factory(u'form',
                       name='editform',
                       props={'action': self.nodeurl})
        form['name'] = factory(
            'field:error:label:text',
            value = self.model.__name__,
            props = {
                'label': 'Name',
            })
        form['save'] = factory(
            'submit',
            props = {
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
                'label': 'Save',
            })
        self.form = form


@tile('editform', interface=IGroup, permission="view")
class GroupEditForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart
    
    def save(self, widget, data):
        pass