from cone.ugm.events import GroupDeletedEvent
from cone.ugm.events import UserDeletedEvent
from cone.ugm.model.group import Group
from cone.ugm.model.user import User
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from zope.event import notify


_ = TranslationStringFactory('cone.ugm')


###############################################################################
# local manager manage membership validation
###############################################################################

LM_TARGET_GID_NOT_ALLOWED = 0
LM_TARGET_UID_NOT_ALLOWED = 1
LM_TARGET_GID_IS_DEFAULT = 2


class ManageMembershipError(Exception):

    def __init__(self, reason, data):
        self.reason = reason
        self.data = data


def validate_add_users_to_groups(model, user_ids, group_ids):
    if not model.local_manager_consider_for_user:
        return
    lm_gids = model.local_manager_target_gids
    for group_id in group_ids:
        if group_id not in lm_gids:
            raise ManageMembershipError(LM_TARGET_GID_NOT_ALLOWED, group_id)
    lm_uids = model.local_manager_target_uids
    for user_id in user_ids:
        if user_id not in lm_uids:
            raise ManageMembershipError(LM_TARGET_UID_NOT_ALLOWED, user_id)


def validate_remove_users_from_groups(model, user_ids, group_ids):
    if not model.local_manager_consider_for_user:
        return
    lm_gids = model.local_manager_target_gids
    for group_id in group_ids:
        if group_id not in lm_gids:
            raise ManageMembershipError(LM_TARGET_GID_NOT_ALLOWED, group_id)
    lm_uids = model.local_manager_target_uids
    for user_id in user_ids:
        if user_id not in lm_uids:
            raise ManageMembershipError(LM_TARGET_UID_NOT_ALLOWED, user_id)
    adm_gid = model.local_manager_gid
    for group_id in group_ids:
        if model.local_manager_is_default(adm_gid, group_id):
            raise ManageMembershipError(LM_TARGET_GID_IS_DEFAULT, group_id)


###############################################################################
# Actions for User application node
###############################################################################

@view_config(
    name='delete_item',
    accept='application/json',
    renderer='json',
    context=User,
    permission='delete_user')
def delete_user_action(model, request):
    """Delete user from database.
    """
    try:
        users = model.parent.backend
        uid = model.model.name
        user = model.model
        del users[uid]
        users()
        notify(UserDeletedEvent(principal=user))
        model.parent.invalidate()
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'delete_user_from_database',
            default="Deleted user '${uid}' from database.",
            mapping={'uid': uid}
        ))
        return {
            'success': True,
            'message': message
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


@view_config(
    name='add_item',
    accept='application/json',
    renderer='json',
    context=User,
    permission='manage_membership')
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
        validate_add_users_to_groups(model, [user.id], group_ids)
        groups = user.root.groups
        for group_id in group_ids:
            groups[group_id].add(user.name)
        groups()
        model.parent.invalidate(user.name)
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'added_user_to_group',
            default="Added user '${uid}' to group '${gid}'.",
            mapping={
                'uid': user.id,
                'gid': ', '.join(group_ids)
            }
        ))
        return {
            'success': True,
            'message': message
        }
    except ManageMembershipError as e:
        if e.reason is not LM_TARGET_GID_NOT_ALLOWED:
            raise Exception(u"Unknown ManageMembershipError reason.")
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'lm_add_target_gid_not_allowed',
            default=(
                "Failed adding user '${uid}' to group '${gid}'. "
                "Manage membership denied for target group."
            ),
            mapping={
                'uid': user.id,
                'gid': e.data
            }
        ))
        return {
            'success': False,
            'message': message
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


@view_config(
    name='remove_item',
    accept='application/json',
    renderer='json',
    context=User,
    permission='manage_membership')
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
        validate_remove_users_from_groups(model, [user.id], group_ids)
        groups = user.root.groups
        for group_id in group_ids:
            del groups[group_id][user.name]
        groups()
        model.parent.invalidate(user.name)
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'removed_user_from_group',
            default="Removed user '${uid}' from group '${gid}'.",
            mapping={
                'uid': user.id,
                'gid': ', '.join(group_ids)
            }
        ))
        return {
            'success': True,
            'message': message
        }
    except ManageMembershipError as e:
        localizer = get_localizer(request)
        if e.reason is LM_TARGET_GID_NOT_ALLOWED:
            message = localizer.translate(_(
                'lm_remove_target_gid_not_allowed',
                default=(
                    "Failed removing user '${uid}' from group '${gid}'. "
                    "Manage membership denied for target group."),
                mapping={
                    'uid': user.id,
                    'gid': e.data
                }
            ))
        elif e.reason is LM_TARGET_GID_IS_DEFAULT:
            message = localizer.translate(_(
                'lm_remove_target_gid_is_default',
                default=(
                    "Failed removing user '${uid}' from group '${gid}'. "
                    "Target group is default group of user."
                ),
                mapping={
                    'uid': user.id,
                    'gid': e.data
                }
            ))
        else:
            raise Exception(u"Unknown ManageMembershipError reason.")
        return {
            'success': False,
            'message': message
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


###############################################################################
# Actions for Group application node
###############################################################################

@view_config(
    name='delete_item',
    accept='application/json',
    renderer='json',
    context=Group,
    permission='delete_group')
def delete_group_action(model, request):
    """Delete group from database.
    """
    try:
        groups = model.parent.backend
        uid = model.model.name
        del groups[uid]
        groups()
        notify(GroupDeletedEvent(principal=model.model))
        model.parent.invalidate()
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
    localizer = get_localizer(request)
    message = localizer.translate(_(
        'deleted_group',
        default='Deleted group from database'
    ))
    return {
        'success': True,
        'message': message
    }


@view_config(
    name='add_item',
    accept='application/json',
    renderer='json',
    context=Group,
    permission='manage_membership')
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
        validate_add_users_to_groups(model, user_ids, [group.id])
        for user_id in user_ids:
            group.add(user_id)
        group()
        model.parent.invalidate(group.name)
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'added_user_to_group',
            default="Added user '${uid}' to group '${gid}'.",
            mapping={
                'uid': ', '.join(user_ids),
                'gid': group.id
            }
        ))
        return {
            'success': True,
            'message': message
        }
    except ManageMembershipError as e:
        if e.reason is not LM_TARGET_UID_NOT_ALLOWED:
            raise Exception(u"Unknown ManageMembershipError reason.")
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'lm_add_target_uid_not_allowed',
            default=(
                "Failed adding user '${uid}' to group '${gid}'. "
                "Manage membership denied for user."
            ),
            mapping={
                'uid': e.data,
                'gid': group.id
            }
        ))
        return {
            'success': False,
            'message': message
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


@view_config(
    name='remove_item',
    accept='application/json',
    renderer='json',
    context=Group,
    permission='manage_membership')
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
        validate_remove_users_from_groups(model, user_ids, [group.id])
        for user_id in user_ids:
            del group[user_id]
        group()

        model.parent.invalidate(group.name)
        localizer = get_localizer(request)
        message = localizer.translate(_(
            'removed_user_from_group',
            default="Removed user '${uid}' from group '${gid}'.",
            mapping={
                'uid': ', '.join(user_ids),
                'gid': group.id
            }
        ))
        return {
            'success': True,
            'message': message
        }
    except ManageMembershipError as e:
        localizer = get_localizer(request)
        if e.reason is LM_TARGET_UID_NOT_ALLOWED:
            message = localizer.translate(_(
                'lm_remove_target_uid_not_allowed',
                default=(
                    "Failed removing user '${uid}' from group '${gid}'. "
                    "Manage membership denied for user."
                ),
                mapping={
                    'uid': e.data,
                    'gid': group.id
                }
            ))
        elif e.reason is LM_TARGET_GID_IS_DEFAULT:
            message = localizer.translate(_(
                'lm_remove_target_gid_is_default',
                default=(
                    "Failed removing user '${uid}' from group '${gid}'. "
                    "Target group is default group of user."
                ),
                mapping={
                    'uid': ', '.join(user_ids),
                    'gid': e.data
                }
            ))
        else:
            raise Exception(u"Unknown ManageMembershipError reason.")
        return {
            'success': False,
            'message': message
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
