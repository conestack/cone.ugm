from pyramid.view import view_config
from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
)
from cone.ugm.model.user import User
from cone.ugm.model.group import Group

_ = TranslationStringFactory('cone.ugm')


###############################################################################
# Actions for User application node
###############################################################################

@view_config(name='delete_item', accept='application/json',
             renderer='json', context=User, permission='delete_user')
def delete_user_action(model, request):
    """Delete user from database.
    """
    try:
        users = model.parent.backend
        uid = model.model.name
        del users[uid]
        users()
        model.parent.invalidate()
        localizer = get_localizer(request)
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
def user_add_to_group_action(model, request):
    """Add user to group.
    """
    group_id = request.params.get('id')
    if not group_id:
        group_ids = request.params.getall('id[]')
    else:
        group_ids = [group_id]
    try:
        user = model.model
        groups = user.root.groups
        for group_id in group_ids:
            groups[group_id].add(user.name)
        groups()
        model.parent.invalidate(user.name)
        localizer = get_localizer(request)
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
def user_remove_from_group_action(model, request):
    """Remove user from group.
    """
    group_id = request.params.get('id')
    if not group_id:
        group_ids = request.params.getall('id[]')
    else:
        group_ids = [group_id]
    try:
        user = model.model
        groups = user.root.groups
        for group_id in group_ids:
            del groups[group_id][user.name]
        groups()
        model.parent.invalidate(user.name)
        localizer = get_localizer(request)
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
def delete_group_action(model, request):
    """Delete group from database.
    """
    try:
        groups = model.parent.backend
        uid = model.model.name
        del groups[uid]
        groups()
        model.parent.invalidate()
    except Exception, e:
        return {
            'success': False,
            'message': str(e),
        }
    localizer = get_localizer(request)
    message = localizer.translate(_('deleted_group',
                                    'Deleted group from database'))
    return {
        'success': True,
        'message': message,
    }


@view_config(name='add_item', accept='application/json',
             renderer='json', context=Group, permission='manage_membership')
def group_add_user_action(model, request):
    """Add user to group.
    """
    user_id = request.params.get('id')
    if not user_id:
        user_ids = request.params.getall('id[]')
    else:
        user_ids = [user_id]
    try:
        group = model.model
        for user_id in user_ids:
            group.add(user_id)
        group()
        model.parent.invalidate(group.name)
        localizer = get_localizer(request)
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
def group_remove_user_action(model, request):
    """Remove user from group.
    """
    user_id = request.params.get('id')
    if not user_id:
        user_ids = request.params.getall('id[]')
    else:
        user_ids = [user_id]
    try:
        group = model.model
        for user_id in user_ids:
            del group[user_id]
        group()
        model.parent.invalidate(group.name)
        localizer = get_localizer(request)
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