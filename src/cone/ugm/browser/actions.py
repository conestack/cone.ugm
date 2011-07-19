from pyramid.view import view_config
from cone.ugm.model.user import User
from cone.ugm.model.group import Group


class Action(object):
    """Abstract action.

    A Subclass must implement ``__call__`` and is supposed to be registetred
    as JSON view, like:

    @view_config(name='action_id', accept='application/json', renderer='json')
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

@view_config(name='delete_item', accept='application/json',
             renderer='json', context=User, permission='delete')
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
            'message': "Deleted user '%s' from database." % id,
        }


@view_config(name='add_item', accept='application/json',
             renderer='json', context=User, permission='edit')
class UserAddToGroupAction(Action):

    def __call__(self):
        """Add user to group.
        """
        group_id = self.request.params.get('id')
        try:
            # XXX: self.model.model is weird naming
            user = self.model.model
            group = user.root.groups[group_id]
            group[user.name] = user
            self.model()
            self.model.parent.invalidate()
            return {
                'success': True,
                'message': "Added user '%s' to group '%s'." % \
                    (user.id, group_id),
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }


@view_config(name='remove_item', accept='application/json',
             renderer='json', context=User, permission='edit')
class UserRemoveFromGroupAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        # XXX: use mechanism from LDAP Groups
        group_id = self.request.params.get('id')
        try:
            user = self.model.model
            group = user.root.groups[group_id]
            del group[user.name]
            self.model()
            # XXX: this feels bad and makes problems, see in invalidate()
            #      Does it? Maybe not any longer.
            self.model.parent.invalidate()
            return {
                'success': True,
                'message': "Removed user '%s' from group '%s'." % \
                    (user.id, group_id),
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }


###############################################################################
# Actions for IGroup application node
###############################################################################

@view_config(name='delete_item', accept='application/json',
             renderer='json', context=Group, permission='delete')
class DeleteGroupAction(Action):

    def __call__(self):
        """Delete group from database.
        """
        groups = self.model.__parent__.ldap_groups
        id = self.model.model.__name__
        del groups[id]
        try:
            groups.context()
            groups = self.model.__parent__.invalidate()
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }
        return {
            'success': True,
            'message': 'Deleted group from database',
        }


@view_config(name='add_item', accept='application/json',
             renderer='json', context=Group, permission='edit')
class GroupAddUserAction(Action):

    def __call__(self):
        """Add user to group.
        """
        user_id = self.request.params.get('id')
        try:
            user_id = self.request.params.get('id')
            group = self.model.model
            user = group.root.users[user_id]
            group[user_id] = user
            self.model()
            self.model.parent.invalidate()
            return {
                'success': True,
                'message': 'Added user to group',
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }


@view_config(name='remove_item', accept='application/json',
             renderer='json', context=Group, permission='edit')
class GroupRemoveUserAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        user_id = self.request.params.get('id')
        try:
            group = self.model.model
            del group[user_id]
            self.model()
            self.model.parent.invalidate()
            return {
                'success': True,
                'message': 'Removed user from group',
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }
