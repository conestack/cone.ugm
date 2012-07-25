from pyramid.view import view_config
from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
)
from cone.ugm.model.user import User
from cone.ugm.model.group import Group

_ = TranslationStringFactory('cone.ugm')


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
             renderer='json', context=User, permission='delete_user')
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
            localizer = get_localizer(self.request)
            message = localizer.translate(
                _('delete_user_from_database',
                  default="Deleted user '${uid}' from database.",
                  mapping={'uid': uid}))
            return {
                'success': True,
                'message': message,
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
            localizer = get_localizer(self.request)
            message = localizer.translate(
                _('added_user_to_group',
                  default="Added user '${uid}' to group '${gid}'.",
                  mapping={
                      'uid': user.id,
                      'gid': group_id
                  }))
            return {
                'success': True,
                'message': message,
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
            localizer = get_localizer(self.request)
            message = localizer.translate(
                _('removed_user_from_group',
                  default="Removed user '${uid}' from group '${gid}'.",
                  mapping={
                      'uid': user.id,
                      'gid': group_id
                  }))
            return {
                'success': True,
                'message': message,
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
             renderer='json', context=Group, permission='delete_group')
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
        localizer = get_localizer(self.request)
        message = localizer.translate(_('deleted_group',
                                        'Deleted group from database'))
        return {
            'success': True,
            'message': message,
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
            localizer = get_localizer(self.request)
            message = localizer.translate(_('group_added_user',
                                            'Added user to group'))
            return {
                'success': True,
                'message': message,
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
            localizer = get_localizer(self.request)
            message = localizer.translate(_('group_removed_user',
                                            'Removed user from group'))
            return {
                'success': True,
                'message': message,
            }
        except Exception, e:
            return {
                'success': False,
                'message': str(e),
            }