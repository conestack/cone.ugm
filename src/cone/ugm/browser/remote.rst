cone.ugm.browser.remote
=======================

Remote calls for 3rd party integration::

    >>> from pyramid.view import render_view_to_response
    >>> from cone.app import root
    >>> users = root['users']

    >>> layer.login('viewer')
    
    >>> request = layer.new_request(type='json')
    >>> request.params['id'] = ''
    
    >>> render_view_to_response(users, request, name='remote_add_user')
    Traceback (most recent call last):
      ...
    HTTPForbidden: 
    Unauthorized: <function remote_add_user at ...> 
    failed permission check
    
    >>> layer.login('manager')
    >>> res = render_view_to_response(users, request, name='remote_add_user')
    
    >>> res.body
    '{"message": "No user ID given.", "success": false}'
    
    >>> layer.logout()