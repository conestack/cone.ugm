from cone.ugm.model.users import Users
from cone.ugm.utils import general_settings
from pyramid.view import view_config


@view_config(
    name='remote_add_user',
    accept='application/json',
    renderer='json',
    context=Users,
    permission='add_user')
def remote_add_user(model, request):
    """Add user via remote service.

    Returns a JSON response containing success state and a message indicating
    what happened::

    {
        success: true, // respective false
        message: 'message'
    }

    Expected request parameters:

    id
        New user id.

    password
        User password to be set initially (optional).

    roles
        Comma seperated role names the user initially has.

    groups
        Comma seperated groups names the user should initially be member of.

    attr.*
        User attributes to be set. I.e. ``attr.mail`` would set the mail
        attribute for newly created user. All request parameters prefixed with
        ``attr`` get checked against user attribute attrmap from settings.

        Restrictions - All values, whether single or multi valued, are passed
        as string or list of strings to the create function.
    """
    params = request.params
    uid = params.get('id')

    if not uid:
        return {
            'success': False,
            'message': u"No user ID given.",
        }

    users = model.backend
    if uid in users:
        return {
            'success': False,
            'message': u"User with given ID already exists.",
        }

    password = params.get('password')

    add_roles = params.get('roles', '')
    add_roles = [val.strip() for val in add_roles.split(',') if val]

    add_groups = params.get('groups', '')
    add_groups = [val.strip() for val in add_groups.split(',') if val]

    attrs = dict()
    for key, val in params.items():
        if not key.startswith('attr.'):
            continue
        key = key[key.find('.') + 1:]
        attrs[key] = val

    settings = general_settings(model)
    attrmap = settings.attrs.users_form_attrmap
    exposed = settings.attrs.users_exposed_attributes
    if not exposed:
        exposed = list()
    valid_attrs = attrmap.keys() + exposed
    checked_attrs = dict()
    for key in valid_attrs:
        val = attrs.get(key)
        if not val:
            continue
        checked_attrs[key] = val

    try:
        user = users.create(uid, **checked_attrs)
        message = u""

        from cone.app.security import DEFAULT_ROLES
        available_roles = [role[0] for role in DEFAULT_ROLES]
        for role in add_roles:
            if role not in available_roles:
                message += u"Role '%s' given but inexistent. " % role
                continue
            user.add_role(role)

        groups = users.parent.groups
        for group in add_groups:
            if group not in groups:
                message += u"Group '%s' given but inexistent. " % group
                continue
            groups[group].add(uid)

        users.parent()

        if password is not None:
            users.passwd(uid, None, password)

        message += u"Created user with ID '%s'." % uid
        return {
            'success': True,
            'message': message,
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
        }
    finally:
        model.invalidate()


@view_config(
    name='remote_delete_user',
    accept='application/json',
    renderer='json',
    context=Users,
    permission='delete_user')
def remote_delete_user(model, request):
    """Remove user via remote service.

    Returns a JSON response containing success state and a message indicating
    what happened::

    {
        success: true, // respective false
        message: 'message'
    }

    Expected request parameters:

    id
        Id of user to delete.
    """
    params = request.params
    uid = params.get('id')

    if not uid:
        return {
            'success': False,
            'message': u"No user ID given.",
        }

    users = model.backend
    if uid not in users:
        return {
            'success': False,
            'message': u"User with given ID not exists.",
        }

    try:
        del users[uid]
        users.parent()

        message = u"Deleted user with ID '%s'." % uid
        return {
            'success': True,
            'message': message,
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
        }
    finally:
        model.invalidate()
