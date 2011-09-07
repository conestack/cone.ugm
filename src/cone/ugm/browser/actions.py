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
# Actions for User application node
###############################################################################

@view_config(name='delete_item', accept='application/json',
             renderer='json', context=User, permission='delete')
class DeleteUserAction(Action):

    def __call__(self):
        """Delete user from database.
        """
        try:
            users = self.model.parent.backend
            uid = self.model.model.name
            del users[uid]
            users()
            self.model.parent.invalidate()
            return {
                'success': True,
                'message': "Deleted user '%s' from database." % uid,
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }


@view_config(name='add_item', accept='application/json',
             renderer='json', context=User, permission='manage_membership')
class UserAddToGroupAction(Action):

    def __call__(self):
        """Add user to group.
        """
        params = self.request.params
        group_id = params.get('id')
        if not group_id:
            group_ids = params.getall('id[]')
        else:
            group_ids = [group_id]
        try:
            user = self.model.model
            groups = user.root.groups
            for group_id in group_ids:
                groups[group_id].add(user.name)
            groups()
            self.model.parent.invalidate(user.name)
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
             renderer='json', context=User, permission='manage_membership')
class UserRemoveFromGroupAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        params = self.request.params
        group_id = params.get('id')
        if not group_id:
            group_ids = params.getall('id[]')
        else:
            group_ids = [group_id]
        try:
            user = self.model.model
            groups = user.root.groups
            for group_id in group_ids:
                del groups[group_id][user.name]
            groups()
            self.model.parent.invalidate(user.name)
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
# Actions for Group application node
###############################################################################

@view_config(name='delete_item', accept='application/json',
             renderer='json', context=Group, permission='delete')
class DeleteGroupAction(Action):

    def __call__(self):
        """Delete group from database.
        """
        try:
            groups = self.model.parent.backend
            uid = self.model.model.name
            del groups[uid]
            groups()
            self.model.parent.invalidate()
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
             renderer='json', context=Group, permission='manage_membership')
class GroupAddUserAction(Action):

    def __call__(self):
        """Add user to group.
        """
        params = self.request.params
        user_id = params.get('id')
        if not user_id:
            user_ids = params.getall('id[]')
        else:
            user_ids = [user_id]
        try:
            group = self.model.model
            for user_id in user_ids:
                group.add(user_id)
            group()
            self.model.parent.invalidate(group.name)
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
             renderer='json', context=Group, permission='manage_membership')
class GroupRemoveUserAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        params = self.request.params
        user_id = params.get('id')
        if not user_id:
            user_ids = params.getall('id[]')
        else:
            user_ids = [user_id]
        try:
            group = self.model.model
            for user_id in user_ids:
                del group[user_id]
            group()
            self.model.parent.invalidate(group.name)
            return {
                'success': True,
                'message': 'Removed user from group',
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }