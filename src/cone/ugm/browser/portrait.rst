Portrait Widget
---------------

::

    >>> from cone.tile import render_tile
    >>> from cone.app import get_root
    >>> from cone.ugm.model.user import User
    >>> from cone.ugm.model.utils import ugm_general

    >>> layer.login('manager')

    >>> root = get_root()
    >>> root['settings']['ugm_general'].invalidate()
    >>> root['settings']['ugm_users'].invalidate()
    >>> root['users'].invalidate()
    >>> users = root['users']
    >>> user = users['uid0']

Portrait related config properties::

    >>> cfg = ugm_general(user)
    >>> cfg.attrs.users_portrait
    u'True'

    >>> cfg.attrs.users_portrait_attr
    u'jpegPhoto'

    >>> cfg.attrs.users_portrait_accept
    u'image/jpeg'

    >>> cfg.attrs.users_portrait_width
    u'50'

    >>> cfg.attrs.users_portrait_height
    u'50'

Portrait enabled, widget is rendered::

    >>> request = layer.new_request()
    >>> res = render_tile(user, request, 'editform')
    >>> res.find('id="input-userform-portrait"') > -1
    True

No portrait, default portrait is shown::

    >>> request = layer.new_request()
    >>> expected = 'src="http://example.com/cone.ugm.static/images/default_portrait.jpg?nocache='
    >>> res.find(expected) > -1
    True

Submit portrait::

    >>> def user_request(model, portrait):
    ...     request = layer.new_request()
    ...     request.params['ajax'] = '1'
    ...     request.params['userform.userPassword'] = '_NOCHANGE_'
    ...     request.params['userform.cn'] = model.attrs['cn']
    ...     request.params['userform.sn'] = model.attrs['sn']
    ...     request.params['userform.mail'] = model.attrs['mail']
    ...     request.params['userform.principal_roles'] = ['viewer', 'editor']
    ...     request.params['userform.portrait'] = portrait
    ...     request.params['action.userform.save'] = '1'
    ...     return request

    >>> import pkg_resources
    >>> from StringIO import StringIO
    >>> def dummy_file_data(filename):
    ...     path = pkg_resources.resource_filename(
    ...         'yafowil.widget.image', 'testing/%s' % filename)
    ...     with open(path) as file:
    ...         data = file.read()
    ...     return data

    >>> dummy_jpg = dummy_file_data('dummy.jpg')
    >>> dummy_jpg
    '\xff\xd8\xff\xe0\x00\x10JFIF\...\xff\xd9'

    >>> portrait = {
    ...     'file': StringIO(dummy_jpg),
    ...     'mimetype': 'image/jpeg',
    ... }

    >>> cfg.attrs.users_portrait
    u'True'

    >>> request = user_request(user, portrait)
    >>> res = render_tile(user, request, 'editform')

New portrait set on user::

    >>> user.attrs.items()
    [('login', u'uid0'), 
    ('userPassword', u'secret0'), 
    ('sn', u'sn0'), 
    ('mail', u'uid0@users300.my-domain.com'), 
    ('cn', u'cn0'), 
    (u'jpegPhoto', '\xff\xd8\xff\xe0\x00\x10JFIF\...\x07\xff\xd9')]

Portrait present, link to user portrait is shown::

    >>> request = layer.new_request()
    >>> res = render_tile(user, request, 'editform')
    >>> expected = 'src="http://example.com/users/uid0/portrait_image?nocache='
    >>> res.find(expected) > -1
    True

Portrait disabled, widget is skipped::

    >>> cfg.attrs.users_portrait = u'False'
    >>> cfg()

    >>> request = layer.new_request()
    >>> res = render_tile(user, request, 'editform')
    >>> res.find('id="input-userform-portrait"') > -1
    False

    >>> cfg.attrs.users_portrait = u'True'
    >>> cfg()

    >>> layer.logout()
