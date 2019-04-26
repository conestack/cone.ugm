cone.ugm.browser.actions
========================

::

    >>> from pyramid.view import render_view_to_response
    >>> from cone.app import root
    >>> users = root['users']
    >>> groups = root['groups']

Test GroupAddUserAction::

    >>> layer.login('viewer')

    >>> request = layer.new_request(type='json')
    >>> request.params['id'] = 'uid99'
    >>> group = groups['group99']

    >>> render_view_to_response(group, request, name='add_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: group_add_user_action failed 
    permission check

    >>> layer.login('editor')
    >>> res = render_view_to_response(group, request, name='add_item')
    >>> res
    <Response at ... 200 OK>

    >>> res.body
    '{"message": "Added user \'uid99\' to group \'group99\'.", "success": true}'

    >>> request.params['id'] = 'uid100'
    >>> res = render_view_to_response(group, request, name='add_item')
    >>> res.body
    '{"message": "u\'uid100\'", "success": false}'

    >>> group.model.users
    [<User object 'uid99' at ...>]

    >>> layer.logout()

Test GroupRemoveUserAction::

    >>> layer.login('viewer')

    >>> render_view_to_response(group, request, name='remove_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: group_remove_user_action failed 
    permission check

    >>> layer.login('editor')
    >>> res = render_view_to_response(group, request, name='remove_item')
    >>> res.body
    '{"message": "u\'uid100\'", "success": false}'

    >>> request.params['id'] = 'uid99'
    >>> res = render_view_to_response(group, request, name='remove_item')
    >>> res.body
    '{"message": "Removed user \'uid99\' from group \'group99\'.", "success": true}'

    >>> group.model.users
    []

    >>> layer.logout()

Test UserAddToGroupAction::

    >>> layer.login('viewer')

    >>> user = users['uid99']
    >>> render_view_to_response(user, request, name='add_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: user_add_to_group_action failed 
    permission check

    >>> layer.login('editor')
    >>> request.params['id'] = 'group99'
    >>> res = render_view_to_response(user, request, name='add_item')
    >>> res.body
    '{"message": "Added user \'uid99\' to group \'group99\'.", "success": true}'

    >>> request.params['id'] = 'group100'
    >>> res = render_view_to_response(user, request, name='add_item')
    >>> res.body
    '{"message": "u\'group100\'", "success": false}'

    >>> user.model.groups
    [<Group object 'group99' at ...>]

    >>> layer.logout()

Test UserRemoveFromGroupAction::

    >>> layer.login('viewer')
    >>> render_view_to_response(user, request, name='remove_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: user_remove_from_group_action failed 
    permission check

    >>> layer.login('editor')
    >>> res = render_view_to_response(user, request, name='remove_item')
    >>> res.body
    '{"message": "u\'group100\'", "success": false}'

    >>> request.params['id'] = 'group99'
    >>> res = render_view_to_response(user, request, name='remove_item')
    >>> res.body
    '{"message": "Removed user \'uid99\' from group \'group99\'.", "success": true}'

    >>> user.model.groups
    []

    >>> layer.logout()

Test DeleteUserAction::

    >>> layer.login('viewer')

    >>> render_view_to_response(user, request, name='delete_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: delete_user_action failed 
    permission check

    >>> layer.login('admin')

    >>> request.params['id'] = 'group99'
    >>> user = users['uid99']
    >>> res = render_view_to_response(user, request, name='add_item')
    >>> user.model.groups
    [<Group object 'group99' at ...>]

    >>> res = render_view_to_response(user, request, name='delete_item')
    >>> res.body
    '{"message": "Deleted user \'uid99\' from database.", "success": true}'

    >>> res = render_view_to_response(user, request, name='delete_item')
    >>> res.body
    '{"message": "u\'uid99\'", "success": false}'

    >>> users['uid99']
    Traceback (most recent call last):
      ...
    KeyError: u'uid99'

    >>> groups['group99'].model.users
    []

    >>> layer.logout()

Test DeleteGroupAction::

    >>> layer.login('viewer')

    >>> group = groups['group99']
    >>> render_view_to_response(group, request, name='delete_item')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: delete_group_action failed 
    permission check

    >>> layer.login('admin')

    >>> res = render_view_to_response(group, request, name='delete_item')
    >>> res.body
    '{"message": "Deleted group from database", "success": true}'

    >>> res = render_view_to_response(group, request, name='delete_item')
    >>> res.body
    '{"message": "u\'group99\'", "success": false}'

    >>> groups.keys()
    [u'group0', u'group1', u'group2', u'group3', u'group4', u'group5', 
    u'group6', u'group7', u'group8', u'group9', u'admin_group_1', 
    u'admin_group_2']

    >>> layer.logout()
