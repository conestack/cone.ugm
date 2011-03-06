from pyramid.view import view_config
from cone.ugm.model.interfaces import IUser
from cone.ugm.model.interfaces import IGroup


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


@view_config(name='add_item', accept='application/json',
          renderer='json', context=IUser, permission="view")
class UserAddToGroupAction(Action):

    def __call__(self):
        """Add user to group.
        """
        # XXX: use mechanism from LDAP Groups
        groups = self.model.root['groups'].ldap_groups
        group_id = self.request.params.get('id')
        path = self.model.model.path
        path.reverse()
        user_dn = 'uid=' + ','.join(path)
        group = groups[group_id]
        if not user_dn in group.attrs['member']:
            members = group.attrs['member']
            members.append(user_dn)
            # group.attrs['member'].append(user_dn) not works
            group.attrs['member'] = members
            group.context()
            self.model.__parent__.invalidate()
        return {
            'success': True,
            'message': 'Added user to group',
        }


@view_config(name='remove_item', accept='application/json',
          renderer='json', context=IUser, permission="view")
class UserRemoveFromGroupAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        # XXX: use mechanism from LDAP Groups
        groups = self.model.root['groups'].ldap_groups
        group_id = self.request.params.get('id')
        path = self.model.model.path
        path.reverse()
        user_dn = 'uid=' + ','.join(path)
        group = groups[group_id]
        if user_dn in group.attrs['member']:
            members = group.attrs['member']
            members.remove(user_dn)
            # group.attrs['member'].remove(user_dn) not works
            group.attrs['member'] = members
            group.context()
            self.model.__parent__.invalidate()
        return {
            'success': True,
            'message': 'Removed User from Group',
        }


###############################################################################
# Actions for IGroup application node
###############################################################################

@view_config(name='delete_item', accept='application/json',
          renderer='json', context=IGroup, permission="view")
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
          renderer='json', context=IGroup, permission="view")
class GroupAddUserAction(Action):

    def __call__(self):
        """Add user to group.
        """
        user_id = self.request.params.get('id')
        group_id = self.model.__name__
        groups = self.model.__parent__.ldap_groups
        group = groups[group_id]
        users = self.model.root['users'].ldap_users
        user = users[user_id]
        path = user.path
        path.reverse()
        user_dn = 'uid=' + ','.join(path)
        if not user_dn in group.attrs['member']:
            members = group.attrs['member']
            members.append(user_dn)
            # group.attrs['member'].append(user_dn) not works
            group.attrs['member'] = members
            group.context()
            self.model.__parent__.invalidate()
        return {
            'success': True,
            'message': 'Added user to group',
        }


@view_config(name='remove_item', accept='application/json',
          renderer='json', context=IGroup, permission="view")
class GroupRemoveUserAction(Action):

    def __call__(self):
        """Remove user from group.
        """
        # XXX: use mechanism from LDAP Groups
        user_id = self.request.params.get('id')
        group_id = self.model.__name__
        groups = self.model.__parent__.ldap_groups
        group = groups[group_id]
        users = self.model.root['users'].ldap_users
        user = users[user_id]
        path = user.path
        path.reverse()
        user_dn = 'uid=' + ','.join(path)
        if user_dn in group.attrs['member']:
            members = group.attrs['member']
            members.remove(user_dn)
            # group.attrs['member'].remove(user_dn) not works
            group.attrs['member'] = members
            group.context()
            self.model.__parent__.invalidate()
        return {
            'success': True,
            'message': 'Removed user from group',
        }
