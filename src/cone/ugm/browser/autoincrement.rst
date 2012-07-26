Autoincrement support
---------------------

::
    >>> from cone.tile import render_tile
    >>> from cone.app import get_root
    >>> from cone.app.model import BaseNode
    >>> from cone.ugm.model.user import User
    >>> from cone.ugm.model.utils import ugm_general
    
    >>> layer.login('manager')
    
    >>> root = get_root()
    >>> users = root['users']
    >>> user = users['uid0']
    
    >>> cfg = ugm_general(user)
    >>> cfg.attrs.user_id_autoincrement
    u'False'
    
    >>> cfg.attrs.user_id_autoincrement_prefix
    u''
    
    >>> def user_vessel(users):
    ...     vessel = User(BaseNode(), None, None)
    ...     vessel.__parent__ = users
    ...     return vessel
    
    >>> vessel = user_vessel(users)
    >>> request = layer.new_request()
    >>> render_tile(vessel, request, 'addform')
    u'...<input class="required text" id="input-userform-id" 
    name="userform.id" required="required" type="text" value="" />...'
    
    >>> cfg.attrs.user_id_autoincrement = u'True'
    >>> cfg()
    
    >>> vessel = user_vessel(users)
    >>> render_tile(vessel, request, 'addform')
    u'...<input class="text" disabled="disabled" id="input-userform-id" 
    name="userform.id" type="text" value="auto incremented" />...'
    
    >>> def user_request(cn, sn, mail):
    ...     request = layer.new_request()
    ...     request.params['userform.id'] = ''
    ...     request.params['userform.userPassword'] = '123456'
    ...     request.params['userform.cn'] = cn
    ...     request.params['userform.sn'] = sn
    ...     request.params['userform.mail'] = mail
    ...     request.params['userform.principal_roles'] = ['viewer', 'editor']
    ...     request.params['action.userform.save'] = '1'
    ...     return request
    
    >>> request = user_request('Sepp Unterwurzacher', 'Sepp',
    ...                        'sepp@unterwurzacher.org')
    >>> vessel = user_vessel(users)
    >>> res = render_tile(vessel, request, 'addform')
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'viewer', u'editor', u'admin', u'manager', u'max', 
    u'sepp', u'localmanager_1', u'localmanager_2', u'uid99', u'uid100', 
    u'uid101', u'100']
    
    >>> request = user_request('Franz Hinterhuber', 'Franz',
    ...                        'franz@hinterhuber.org')
    >>> vessel = user_vessel(users)
    >>> res = render_tile(vessel, request, 'addform')
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'viewer', u'editor', u'admin', u'manager', u'max', 
    u'sepp', u'localmanager_1', u'localmanager_2', u'uid99', u'uid100', 
    u'uid101', u'100', u'101']
    
    >>> cfg.attrs.user_id_autoincrement_prefix = u'uid'
    >>> cfg()
    
    >>> request = user_request('Ander Er', 'Ander', 'ander@er.org')
    >>> vessel = user_vessel(users)
    >>> res = render_tile(vessel, request, 'addform')
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'viewer', u'editor', u'admin', u'manager', u'max', 
    u'sepp', u'localmanager_1', u'localmanager_2', u'uid99', u'uid100', 
    u'uid101', u'100', u'101', u'uid102']
    
    >>> cfg.attrs.user_id_autoincrement_prefix = u'admin'
    >>> cfg()
    
    >>> request = user_request('Hirs Schneider', 'Hirs', 'hirs@schneider.org')
    >>> vessel = user_vessel(users)
    >>> res = render_tile(vessel, request, 'addform')
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'viewer', u'editor', u'admin', u'manager', u'max', 
    u'sepp', u'localmanager_1', u'localmanager_2', u'uid99', u'uid100', 
    u'uid101', u'100', u'101', u'uid102', u'admin100']

Cleanup::

    >>> del users[u'100']
    >>> del users[u'101']
    >>> del users[u'uid102']
    >>> del users[u'admin100']
    
    >>> users()

    >>> cfg.attrs.user_id_autoincrement = u'False'
    >>> cfg.attrs.user_id_autoincrement_prefix = u''
    >>> cfg()
   
    >>> layer.logout()
