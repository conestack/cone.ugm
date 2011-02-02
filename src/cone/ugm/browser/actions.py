from pyramid.view import bfg_view
from cone.ugm.model.interfaces import IUser
from cone.ugm.model.interfaces import IGroup

class Action(object):
    """Abstract action.
    
    A Subclass must implement ``__call__`` and is supposed to be registetred
    as JSON bfg view, like:
    
    @bfg_view(name='action_id', accept='application/json', renderer='json')
    """
    
    def __init__(self, model, request):
        self.model = model
        self.request = request
    
    def __call__(self):
        """Perform this action and return JSON response.
        
        Returns a dict with success flag and return message:
            {
                'success': True,
                'message': 'Return message',
            }
        """
        raise NotImplementedError(u"Abstract action does not implement "
                                  u"``__call__``.")

###############################################################################
# Actions for IUser application node
###############################################################################

@bfg_view(name='delete_item', accept='application/json',
          renderer='json', context=IUser, permission="view")
class DeleteUserAction(Action):
    
    def __call__(self):
        """Delete user from database.
        """
        users = self.model.__parent__.ldap_users
        id = self.model.model.__name__
        del users[id]
        try:
            users.context()
            users = self.model.__parent__.invalidate()
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }
        return {
            'success': True,
            'message': 'Deleted user %s from database' % id,
        }

@bfg_view(name='add_item', accept='application/json',
          renderer='json', context=IUser, permission="view")
class UserAddToGroupAction(Action):
    
    def __call__(self):
        """Add user to group.
        """
        return {
            'success': True,
            'message': 'Added user to group',
        }

@bfg_view(name='remove_item', accept='application/json',
          renderer='json', context=IUser, permission="view")
class UserRemoveFromGroupAction(Action):
    
    def __call__(self):
        """Remove user from group.
        """
        return {
            'success': True,
            'message': 'Removed User from Group',
        }

###############################################################################
# Actions for IGroup application node
###############################################################################

@bfg_view(name='delete_item', accept='application/json',
          renderer='json', context=IGroup, permission="view")
class DeleteGroupAction(Action):
    
    def __call__(self):
        """Delete group from database.
        """
        return {
            'success': True,
            'message': 'Deleted group from database',
        }

@bfg_view(name='add_item', accept='application/json',
          renderer='json', context=IGroup, permission="view")
class GroupAddUserAction(Action):
    
    def __call__(self):
        """Add user to group.
        """
        return {
            'success': True,
            'message': 'Added user to group',
        }

@bfg_view(name='remove_item', accept='application/json',
          renderer='json', context=IGroup, permission="view")
class GroupRemoveUserAction(Action):
    
    def __call__(self):
        """Remove user from group.
        """
        return {
            'success': True,
            'message': 'Removed user from group',
        }