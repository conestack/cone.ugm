cone.ugm.browser.group
======================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile
    
    >>> groups = root['groups']
    >>> group = groups['group5']
    
    >>> request = layer.new_request()

Unauthenticated content tile renders login form::

    >>> expected = \
    ...     '<form action="http://example.com/groups/group5/login"'
    >>> res = render_tile(group, request, 'content')
    >>> res.find(expected) > -1
    True

Other tiles raise if unauthenticated::
    
    >>> render_tile(group, request, 'leftcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.group.GroupLeftColumn object at ...> 
    failed permission check
    
    >>> render_tile(group, request, 'rightcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.group.GroupRightColumn object at ...> 
    failed permission check
    
    >>> render_tile(group, request, 'columnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.group.UsersOfGroupColumnListing object at ...> 
    failed permission check
    
    >>> render_tile(group, request, 'allcolumnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.group.AllUsersColumnListing object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('manager')
    
    >>> res = render_tile(group, request, 'leftcolumn')
    >>> res.find('<div class="column left_column box">') > -1
    True
    
    >>> res = render_tile(group, request, 'rightcolumn')
    >>> res.find('<div class="column right_column">') > -1
    True
    
    >>> res = render_tile(group, request, 'columnlisting')
    >>> expected = \
    ...     '<li ajax:target="http://example.com/users/uid5"'
    >>> res.find(expected) > -1
    True
    
    >>> res = render_tile(group, request, 'allcolumnlisting')
    >>> expected = \
    ...     '<li ajax:target="http://example.com/users/uid1"'
    >>> res.find(expected) > -1
    True
    
    >>> expected = \
    ...     '<li ajax:target="http://example.com/users/uid9"'
    >>> res.find(expected) > -1
    True
    
    >>> layer.logout()

Add::
    
    >>> layer.login('viewer')
    
    >>> request = layer.new_request()
    >>> request.params['factory'] = 'group'
    
    >>> res = render_tile(groups, request, 'add')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.app.browser.authoring.AddTile object at ...> 
    failed permission check
    
    >>> layer.login('manager')
    >>> res = render_tile(groups, request, 'add')
    >>> expected = '<form action="http://example.com/groups/add"'
    >>> res.find(expected) > -1
    True
    
    >>> request.params['groupform.id'] = ''
    >>> request.params['groupform.principal_roles'] = []
    >>> request.params['action.groupform.save'] = '1'
    
    >>> res = render_tile(groups, request, 'add')
    >>> res.find('class="errormessage">No Id defined') > -1
    True
    
    >>> request.params['groupform.id'] = 'group99'
    
    >>> res = render_tile(groups, request, 'add')
    >>> res
    u''
    
    >>> request.environ['redirect']
    <HTTPFound at ... 302 Found>
    
    >>> groups.keys()
    [u'group0', u'group1', u'group2', u'group3', u'group4', u'group5', 
    u'group6', u'group7', u'group8', u'group9', u'admin_group_1', 
    u'admin_group_2', u'group99']
    
    >>> group = groups['group99']
    >>> group
    <Group object 'group99' at ...>

Edit::

    >>> request = layer.new_request()
    >>> res = render_tile(group, request, 'edit')
    >>> expected = '<form action="http://example.com/groups/group99/edit"'
    >>> res.find(expected) > -1
    True
    
    >>> layer.logout()
    